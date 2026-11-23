"""
app.py
------
UrbanPulse - AI Traffic Intelligence Platform
Modern dashboard UI (navbar + hero + card-based layout), feature-complete,
with real-time lane-wise vehicle detection, priority + aging adaptive signal control,
traffic prediction, and session analytics.
"""

import os
import sys
import time
from collections import defaultdict
from datetime import datetime

import cv2
import numpy as np
import pandas as pd
import streamlit as st

# Ensure project directory is in python search path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config
import detection
from density import get_lane_status
from signal_control import (
    calculate_green_times, apply_emergency_override, select_next_lane,
    MIN_GREEN,
)
from video_source import get_video_source, read_frame_loop, ensure_demo_videos
import prediction as pred_module
from visuals import (
    inject_css, render_navbar, render_hero, section_label, kpi_card,
    density_badge_html, traffic_light_html, lane_status_html, lane_title_html,
    lane_card_html,
)

DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

LANES = ["lane_1", "lane_2", "lane_3", "lane_4"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ACCENTS = ["#4F46E5", "#10B981", "#F59E0B", "#EC4899"]

st.set_page_config(page_title=config.APP_TITLE, layout="wide", initial_sidebar_state="expanded")
inject_css()

# Pre-generate or ensure demo videos are available
DEMO_PATHS = ensure_demo_videos(DATA_DIR)

# ---------------------------------------------------------------------
# Session state initialisation (replaces persistent database)
# ---------------------------------------------------------------------
defaults = {
    "history": [],
    "vehicle_totals": defaultdict(int),
    "active_lane": LANES[0],
    "active_remaining": MIN_GREEN,
    "wait_times": {lane: 0.0 for lane in LANES},
    "last_tick": None,
    "session_start": None,
    "cycles_run": 0,
    "lane_data": {},
    "is_running": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def log_cycle(lane_data: dict):
    ts = datetime.now().strftime("%H:%M:%S")
    for lane, info in lane_data.items():
        st.session_state.history.append({
            "time": ts,
            "lane": lane,
            "count": info["count"],
            "density": info["density"],
            "green_time": info["green_time"],
        })
    if len(st.session_state.history) > 500:
        st.session_state.history = st.session_state.history[-500:]


nav_ph = st.empty()
render_hero(
    "Real-time signals that think for themselves",
    "Live vehicle detection, lane-wise density, and priority-based adaptive "
    "signal control, running on your own camera or uploaded footage."
)

# =======================================================================
# SIDEBAR
# =======================================================================
st.sidebar.markdown(f"**{config.APP_TITLE}**")
st.sidebar.caption("Control Panel")
st.sidebar.markdown("---")

# Advanced Mode feature toggle
advanced_mode = st.sidebar.checkbox(
    "Advanced Features",
    value=config.ADVANCED_MODE,
    help="Toggle extra features (Analytics tab, 24-Hour Forecast tab, and Emergency Priority override)."
)

st.sidebar.subheader("Quick Prediction")
day_label = st.sidebar.selectbox("Day", DAYS, index=datetime.now().weekday())
hour = st.sidebar.slider("Hour", 0, 23, datetime.now().hour)
day_index = DAYS.index(day_label)
pred_count, pred_level = pred_module.predict_next(day_index, float(hour))
st.sidebar.metric("Predicted vehicle count", pred_count)
st.sidebar.write(f"Expected density: **{pred_level}**")

emergency_lane = "None"
if advanced_mode or config.SHOW_EMERGENCY_OVERRIDE:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Emergency Vehicle Priority")
    emergency_lane = st.sidebar.selectbox(
        "Emergency vehicle detected on:", ["None"] + LANES,
        help="Instantly gives this lane maximum green time and drops all "
             "other lanes to the minimum, so the emergency vehicle can "
             "clear the intersection as fast as possible."
    )

# =======================================================================
# LANE SOURCE SETUP (core feature - always visible)
# =======================================================================
section_label("Lane Source Setup")
with st.expander("Configure video sources for all 4 lanes", expanded=True):
    lane_sources = {}
    setup_cols = st.columns(4)
    for i, lane in enumerate(LANES):
        with setup_cols[i]:
            st.markdown(f"**{lane.replace('_', ' ').title()}**")
            src_type = st.radio("Source", ["Upload Video", "Live Camera"], key=f"src_type_{lane}")
            if src_type == "Live Camera":
                cam_choice = st.text_input("Camera index or RTSP URL", value="0", key=f"cam_{lane}").strip()
                lane_sources[lane] = ("live", int(cam_choice) if cam_choice.isdigit() else (cam_choice if cam_choice else 0))
            else:
                uploaded = st.file_uploader("Upload clip", type=["mp4", "avi", "mov"], key=f"upload_{lane}")
                if uploaded is not None:
                    save_path = os.path.join(TEMP_DIR, f"{lane}.mp4")
                    file_bytes = uploaded.getvalue()
                    if not os.path.exists(save_path) or os.path.getsize(save_path) != len(file_bytes):
                        with open(save_path, "wb") as f:
                            f.write(file_bytes)
                    lane_sources[lane] = ("upload", save_path)
                else:
                    st.caption("No file uploaded. Demo clip will be used.")
                    lane_sources[lane] = ("upload", DEMO_PATHS[i])

col_run, col_stop = st.columns([2, 1])
with col_run:
    run_real = st.checkbox("Start Real-Time Monitoring", key="run_monitoring")

with nav_ph.container():
    render_navbar(config.APP_TITLE, is_live=run_real)

# =======================================================================
# KPI ROW — placeholders so they can be refreshed LIVE during the loop
# =======================================================================
section_label("Overview")
show_advanced_kpis = advanced_mode or config.SHOW_ADVANCED_KPIS
kpi_cols = st.columns(4 if show_advanced_kpis else 3)
kpi_ph = [c.empty() for c in kpi_cols]


def render_kpis():
    current_total = sum(v.get("count", 0) for v in st.session_state.lane_data.values())
    active_lane_name = st.session_state.active_lane.replace("_", " ").title()
    uptime_str = "00:00"
    if st.session_state.session_start:
        secs = int(time.time() - st.session_state.session_start)
        uptime_str = f"{secs // 60:02d}:{secs % 60:02d}"

    with kpi_ph[0].container():
        kpi_card(current_total, "Vehicles (this cycle)", ACCENTS[0])
    with kpi_ph[1].container():
        kpi_card(active_lane_name, "Currently Green", ACCENTS[1])
    with kpi_ph[2].container():
        kpi_card(uptime_str, "Session Uptime", ACCENTS[2])
    if show_advanced_kpis:
        with kpi_ph[3].container():
            kpi_card(sum(st.session_state.vehicle_totals.values()), "Total Detections", ACCENTS[3])


render_kpis()

# =======================================================================
# TABS
# =======================================================================
tab_names = ["Live Monitoring"]
show_analytics = advanced_mode or config.SHOW_ANALYTICS_TAB
show_prediction = advanced_mode or config.SHOW_PREDICTION_TAB

if show_analytics:
    tab_names.append("Analytics")
if show_prediction:
    tab_names.append("24-Hour Forecast")
tab_names.append("About")

tabs = st.tabs(tab_names)
tab_map = dict(zip(tab_names, tabs))


def create_placeholder_frame(text: str = "Signal Unavailable"):
    """Creates a clean blank frame with label if a source is inaccessible."""
    blank = np.full((240, 320, 3), 30, dtype=np.uint8)
    cv2.putText(blank, text, (40, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
    return blank


# -----------------------------------------------------------------------
# TAB: LIVE MONITORING
# -----------------------------------------------------------------------
with tab_map["Live Monitoring"]:
    section_label("Lane Feeds")
    cols = st.columns(4)
    panel_top_ph = [c.empty() for c in cols]
    frame_ph = [c.empty() for c in cols]
    info_ph = [c.empty() for c in cols]
    chart_ph = st.empty()

    if run_real:
        if st.session_state.session_start is None:
            st.session_state.session_start = time.time()
            st.session_state.last_tick = time.time()

        caps = {}
        for lane in LANES:
            caps[lane] = get_video_source(*lane_sources[lane])

        skip_n = 2
        frame_counter = 0
        cycles = 0

        try:
            while run_real and cycles < 400:
                lane_data = {}
                for i, lane in enumerate(LANES):
                    cap = caps.get(lane)
                    ret, frame = read_frame_loop(cap)
                    if not ret or frame is None or frame.size == 0:
                        frame = create_placeholder_frame(f"{lane.replace('_', ' ').title()}")
                        detections = []
                    else:
                        frame = cv2.resize(frame, (320, 240))
                        if frame_counter % skip_n == 0:
                            detections = detection.detect_vehicles(frame)
                            st.session_state[f"last_det_{lane}"] = detections
                            for det in detections:
                                st.session_state.vehicle_totals[det["class"]] += 1
                        else:
                            detections = st.session_state.get(f"last_det_{lane}", [])

                        frame = detection.draw_detections(frame, detections)

                    count, dens = get_lane_status(detections)
                    lane_data[lane] = {"count": count, "density": dens}

                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    panel_top_ph[i].markdown(
                        lane_title_html(lane.replace("_", " ").title(), "Live feed"),
                        unsafe_allow_html=True
                    )
                    frame_ph[i].image(frame_rgb, channels="RGB")

                if lane_data:
                    densities = {lane: info["density"] for lane, info in lane_data.items()}
                    green_times = calculate_green_times(densities)

                    now = time.time()
                    elapsed = now - (st.session_state.last_tick or now)
                    st.session_state.last_tick = now
                    elapsed = max(0.0, min(elapsed, 5.0))

                    # Emergency override handling
                    has_emergency = (
                        (advanced_mode or config.SHOW_EMERGENCY_OVERRIDE)
                        and emergency_lane != "None"
                        and emergency_lane in green_times
                    )
                    if has_emergency:
                        green_times = apply_emergency_override(green_times, emergency_lane)
                        st.session_state.active_lane = emergency_lane
                        st.session_state.active_remaining = green_times[emergency_lane]
                        st.session_state.wait_times[emergency_lane] = 0.0
                    else:
                        st.session_state.active_remaining -= elapsed
                        for lane in LANES:
                            if lane != st.session_state.active_lane:
                                st.session_state.wait_times[lane] = st.session_state.wait_times.get(lane, 0.0) + elapsed

                        if st.session_state.active_remaining <= 0:
                            next_lane = select_next_lane(
                                densities, st.session_state.wait_times,
                                exclude_lane=st.session_state.active_lane,
                            )
                            st.session_state.active_lane = next_lane
                            st.session_state.active_remaining = green_times.get(next_lane, MIN_GREEN)
                            st.session_state.wait_times[next_lane] = 0.0

                    for lane in lane_data:
                        lane_data[lane]["green_time"] = green_times.get(lane, MIN_GREEN)
                    st.session_state.lane_data = lane_data

                    active_lane = st.session_state.active_lane
                    log_cycle(lane_data)
                    st.session_state.cycles_run += 1
                    render_kpis()

                    for i, lane in enumerate(LANES):
                        if lane not in lane_data:
                            continue
                        info = lane_data[lane]
                        is_active = (lane == active_lane)
                        if is_active:
                            light_state = "yellow" if st.session_state.active_remaining <= 3 else "green"
                            status_html = lane_status_html(True, st.session_state.active_remaining)
                        else:
                            light_state = "red"
                            status_html = lane_status_html(False, st.session_state.wait_times.get(lane, 0.0))

                        info_ph[i].markdown(
                            lane_card_html(
                                count=int(info.get("count", 0)),
                                density=str(info.get("density", "Low")),
                                status_html=status_html,
                                green_time=int(info.get("green_time", MIN_GREEN)),
                                light_state=light_state,
                            ),
                            unsafe_allow_html=True
                        )

                    hist_df = pd.DataFrame(st.session_state.history)
                    if not hist_df.empty:
                        pivot = hist_df.pivot_table(
                            index="time", columns="lane",
                            values="count", aggfunc="last"
                        ).tail(25)
                        chart_ph.line_chart(pivot)

                frame_counter += 1
                cycles += 1
                time.sleep(0.05)

        finally:
            for cap in caps.values():
                if cap is not None:
                    cap.release()

        if cycles >= 400:
            st.info("Live cycle batch completed. Re-tick 'Start Real-Time Monitoring' to continue.")
    else:
        # Idle state: render preview cards for all 4 lanes
        for i, lane in enumerate(LANES):
            panel_top_ph[i].markdown(
                lane_title_html(lane.replace("_", " ").title(), "Source configured"),
                unsafe_allow_html=True
            )
            # Try to grab a preview frame
            cap_preview = get_video_source(*lane_sources[lane])
            ret_p, frame_p = read_frame_loop(cap_preview)
            if cap_preview is not None:
                cap_preview.release()

            if ret_p and frame_p is not None and frame_p.size > 0:
                frame_preview_rgb = cv2.cvtColor(cv2.resize(frame_p, (320, 240)), cv2.COLOR_BGR2RGB)
                frame_ph[i].image(frame_preview_rgb, channels="RGB")
            else:
                frame_ph[i].image(create_placeholder_frame(f"{lane.replace('_', ' ').title()}"), channels="RGB")

            info_ph[i].markdown(
                lane_card_html(
                    count=0,
                    density="Low",
                    status_html='<span class="lane-status status-waiting">IDLE · Ready</span>',
                    green_time=MIN_GREEN,
                    light_state="red",
                ),
                unsafe_allow_html=True
            )

        st.info("Check **'Start Real-Time Monitoring'** above to run live vehicle detection and adaptive signal scheduling.")

        # Display chart if previous session history exists
        if st.session_state.history:
            hist_df = pd.DataFrame(st.session_state.history)
            pivot = hist_df.pivot_table(index="time", columns="lane", values="count", aggfunc="last").tail(25)
            chart_ph.line_chart(pivot)

    st.markdown("---")
    section_label("Session History")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history).tail(50), use_container_width=True)
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.caption("No data logged yet this session.")

# -----------------------------------------------------------------------
# TAB: ANALYTICS (advanced)
# -----------------------------------------------------------------------
if show_analytics:
    with tab_map["Analytics"]:
        section_label("Vehicle Type Breakdown")
        totals = dict(st.session_state.vehicle_totals)
        if totals and any(totals.values()):
            df_types = pd.DataFrame({
                "Vehicle Type": list(totals.keys()),
                "Count": list(totals.values())
            }).set_index("Vehicle Type")
            st.bar_chart(df_types)
        else:
            st.caption("No vehicle detections logged yet. Start monitoring on the Live tab first.")

        section_label("Session Statistics")
        hist_df = pd.DataFrame(st.session_state.history)
        if not hist_df.empty:
            s1, s2, s3 = st.columns(3)
            with s1:
                st.metric("Total cycles logged", st.session_state.cycles_run)
            with s2:
                busiest_lane = "lane_1"
                if "count" in hist_df.columns and not hist_df["count"].empty:
                    mean_counts = hist_df.groupby("lane")["count"].mean()
                    if not mean_counts.empty:
                        busiest_lane = str(mean_counts.idxmax())
                st.metric("Busiest lane (avg)", busiest_lane.replace("_", " ").title())
            with s3:
                peak_val = 0
                if "count" in hist_df.columns and not hist_df["count"].empty:
                    counts_list = [int(x) for x in hist_df["count"] if pd.notna(x)]
                    if counts_list:
                        peak_val = max(counts_list)
                st.metric("Peak single-lane count", peak_val)

            section_label("Export Session Report")
            csv = hist_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download session history (CSV)", csv,
                file_name="urbanpulse_session_report.csv", mime="text/csv"
            )
        else:
            st.caption("No history yet. Start monitoring on the Live tab first.")

# -----------------------------------------------------------------------
# TAB: 24-HOUR PREDICTION (advanced)
# -----------------------------------------------------------------------
if show_prediction:
    with tab_map["24-Hour Forecast"]:
        section_label("Full-Day Forecast")
        forecast_day_label = st.selectbox("Select day to forecast", DAYS, key="forecast_day")
        f_day_index = DAYS.index(forecast_day_label)
        hours, preds = pred_module.forecast_day(f_day_index)
        forecast_df = pd.DataFrame({"Hour": hours, "Predicted Vehicles": preds}).set_index("Hour")
        st.line_chart(forecast_df)
        st.caption("Forecast generated by a Random Forest model trained on "
                   "historical traffic patterns (morning + evening peaks, "
                   "lighter weekend volumes).")

# -----------------------------------------------------------------------
# TAB: ABOUT
# -----------------------------------------------------------------------
with tab_map["About"]:
    section_label("About UrbanPulse")
    st.markdown("""
    **UrbanPulse** is an AI-powered traffic intelligence system that replaces
    fixed-timer traffic signals with a real-time, data-driven adaptive control
    system.

    **Pipeline:** CCTV / uploaded video → YOLOv8 vehicle detection →
    lane-wise density estimation → priority-based adaptive signal control →
    dashboard.

    **Lane scheduling:** the lane that turns green next is chosen using a
    priority + aging score. Busier lanes are more likely to be picked
    sooner, while an aging factor guarantees that a lane waiting a long time
    will always eventually get its turn.

    **Tech stack:** Python, OpenCV, YOLOv8 (Ultralytics), Random Forest
    (Scikit-learn), Streamlit.
    """)
