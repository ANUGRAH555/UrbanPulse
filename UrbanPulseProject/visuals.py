"""
visuals.py
----------
Modern, SaaS-dashboard style UI building blocks for UrbanPulse.
Design language: clean whites, soft shadows, an indigo brand accent,
Inter typeface, no emoji glyphs anywhere (text + shape based indicators
instead) — meant to look like a polished product, not a hobby script.
"""

import streamlit as st

DENSITY_COLOR = {"Low": "#10B981", "Medium": "#F59E0B", "High": "#EF4444"}
INDIGO = "#4F46E5"
INDIGO_DARK = "#3730A3"
SLATE_900 = "#0F172A"
SLATE_500 = "#64748B"
SLATE_200 = "#E2E8F0"
BG = "#F8FAFC"


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
    .stApp {
        background-color: """ + BG + """;
        background-image:
            radial-gradient(circle at 8% 12%, rgba(99,102,241,0.10) 0%, rgba(99,102,241,0) 40%),
            radial-gradient(circle at 92% 8%, rgba(79,70,229,0.08) 0%, rgba(79,70,229,0) 35%),
            radial-gradient(circle at 50% 100%, rgba(16,185,129,0.06) 0%, rgba(16,185,129,0) 40%),
            radial-gradient(circle, rgba(15,23,42,0.05) 1px, transparent 1px);
        background-size: auto, auto, auto, 22px 22px;
        background-attachment: fixed;
    }
    #MainMenu, footer, [data-testid="stToolbar"] {visibility: hidden;}
    .block-container { padding-top: 1.4rem; max-width: 1500px; padding-left: 2rem; padding-right: 2rem; }

    /* ---------- NAVBAR ---------- */
    .up-navbar {
        display: flex; align-items: center; justify-content: space-between;
        background: #FFFFFF; border: 1px solid """ + SLATE_200 + """;
        border-radius: 14px; padding: 14px 22px; margin-bottom: 18px;
        box-shadow: 0 1px 3px rgba(15,23,42,0.04);
    }
    .up-brand { display: flex; align-items: center; gap: 14px; }
    .up-logo-mark {
        width: 48px; height: 48px; border-radius: 12px;
        background: linear-gradient(135deg, #6366F1 0%, #4338CA 100%);
        display: flex; align-items: center; justify-content: center;
        color: #FFFFFF; font-weight: 800; font-size: 18px; letter-spacing: -0.5px;
        box-shadow: 0 4px 10px rgba(79,70,229,0.35);
    }
    .up-brand-text h1 {
        font-size: 1.9rem; font-weight: 800; color: """ + SLATE_900 + """;
        margin: 0; letter-spacing: -0.5px; line-height: 1.1;
    }
    .up-brand-text p { font-size: 0.85rem; color: """ + SLATE_500 + """; margin: 2px 0 0 0; }
    .up-status-pill {
        display: flex; align-items: center; gap: 7px;
        background: #F1F5F9; border: 1px solid """ + SLATE_200 + """;
        border-radius: 999px; padding: 6px 14px;
        font-size: 0.78rem; font-weight: 600; color: """ + SLATE_500 + """;
    }
    .up-status-dot { width: 8px; height: 8px; border-radius: 50%; background: #94A3B8; }
    .up-status-dot.live { background: #10B981; box-shadow: 0 0 0 3px rgba(16,185,129,0.18); }

    /* ---------- HERO BANNER ---------- */
    .up-hero {
        background: linear-gradient(120deg, #4338CA 0%, #4F46E5 45%, #6366F1 100%);
        border-radius: 16px; padding: 26px 28px; margin-bottom: 20px;
        box-shadow: 0 10px 24px rgba(67,56,202,0.25);
        position: relative; overflow: hidden;
    }
    .up-hero::after {
        content: ""; position: absolute; right: -40px; top: -60px;
        width: 220px; height: 220px; border-radius: 50%;
        background: rgba(255,255,255,0.08);
    }
    .up-hero h2 {
        color: #FFFFFF; font-size: 2.1rem; font-weight: 800; margin: 0 0 6px 0;
        letter-spacing: -0.6px; position: relative; z-index: 1; line-height: 1.15;
    }
    .up-hero p {
        color: #E0E1FF; font-size: 1rem; margin: 0; max-width: 680px;
        position: relative; z-index: 1;
    }

    /* ---------- SECTION LABEL ---------- */
    .up-section-label {
        display: flex; align-items: center; gap: 8px; margin: 6px 0 12px 0;
    }
    .up-section-dot { width: 8px; height: 8px; border-radius: 2px; background: """ + INDIGO + """; }
    .up-section-label span {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 1.2px;
        color: """ + SLATE_500 + """; text-transform: uppercase;
    }

    /* ---------- KPI CARDS ---------- */
    .kpi-card {
        background: #FFFFFF; border-radius: 14px; padding: 16px 18px 14px 18px;
        border: 1px solid """ + SLATE_200 + """;
        box-shadow: 0 1px 3px rgba(15,23,42,0.04);
        position: relative; overflow: hidden;
    }
    .kpi-card::before {
        content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
        background: var(--accent, """ + INDIGO + """);
    }
    .kpi-card .kpi-value { font-size: 1.55rem; font-weight: 800; color: """ + SLATE_900 + """; line-height: 1.15; }
    .kpi-card .kpi-label {
        color: """ + SLATE_500 + """; font-size: 0.72rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.6px; margin-top: 3px;
    }

    /* ---------- PANEL / CARD WRAPPER ---------- */
    .up-panel {
        background: #FFFFFF; border-radius: 14px; border: 1px solid """ + SLATE_200 + """;
        box-shadow: 0 1px 3px rgba(15,23,42,0.04); padding: 14px 16px 12px 16px;
        margin-top: 8px; margin-bottom: 12px;
    }
    .lane-name {
        font-weight: 700; font-size: 0.98rem; color: """ + SLATE_900 + """; margin-bottom: 2px;
    }
    .lane-sub { font-size: 0.72rem; color: """ + SLATE_500 + """; margin-bottom: 8px; }

    [data-testid="stImage"] img { border-radius: 10px; border: 1px solid """ + SLATE_200 + """; }

    /* ---------- BADGES / PILLS ---------- */
    .density-badge {
        display: inline-block; padding: 3px 11px; border-radius: 7px;
        font-weight: 700; font-size: 0.72rem; color: #FFFFFF; letter-spacing: 0.3px;
    }
    .lane-status {
        font-size: 0.74rem; font-weight: 700; margin-top: 2px;
        padding: 3px 10px; border-radius: 999px; display: inline-block;
    }
    .status-active { background: #D1FAE5; color: #047857; }
    .status-waiting { background: #FEF3C7; color: #92400E; }

    /* ---------- TRAFFIC LIGHT ---------- */
    .traffic-light {
        background: #1E293B; border-radius: 999px; padding: 8px 6px;
        display: flex; flex-direction: column; align-items: center; gap: 6px;
        width: 30px; margin: 0 auto;
        box-shadow: 0 3px 8px rgba(15,23,42,0.25);
    }
    .tl-dot { width: 13px; height: 13px; border-radius: 50%; background: #334155; }
    .tl-red-on { background: #EF4444; box-shadow: 0 0 8px #EF4444; }
    .tl-yellow-on { background: #F59E0B; box-shadow: 0 0 8px #F59E0B; }
    .tl-green-on { background: #10B981; box-shadow: 0 0 8px #10B981; }

    /* ---------- STREAMLIT WIDGET OVERRIDES ---------- */
    div[data-testid="stMetricValue"] { color: """ + SLATE_900 + """; font-weight: 800; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        background: #FFFFFF; border: 1px solid """ + SLATE_200 + """;
        border-radius: 10px 10px 0 0; padding: 8px 18px; font-weight: 600;
        color: """ + SLATE_500 + """;
    }
    .stTabs [aria-selected="true"] { color: """ + INDIGO + """ !important; border-color: """ + INDIGO + """; }
    .streamlit-expanderHeader {
        font-weight: 700; color: """ + SLATE_900 + """; background: #FFFFFF;
        border-radius: 10px;
    }
    div[data-testid="stExpander"] {
        border: 1px solid """ + SLATE_200 + """; border-radius: 12px; background: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)


def render_navbar(title: str, is_live: bool):
    dot_cls = "up-status-dot live" if is_live else "up-status-dot"
    status_text = "Live Monitoring" if is_live else "Idle"
    st.markdown(f"""
    <div class="up-navbar">
        <div class="up-brand">
            <div class="up-logo-mark">UP</div>
            <div class="up-brand-text">
                <h1>{title}</h1>
                <p>AI Traffic Intelligence Platform</p>
            </div>
        </div>
        <div class="up-status-pill"><span class="{dot_cls}"></span>{status_text}</div>
    </div>
    """, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str):
    st.markdown(f"""
    <div class="up-hero">
        <h2>{title}</h2>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def section_label(text: str):
    st.markdown(f"""
    <div class="up-section-label"><span class="up-section-dot"></span><span>{text}</span></div>
    """, unsafe_allow_html=True)


def kpi_card(value, label: str, accent: str = INDIGO):
    st.markdown(f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def density_badge_html(density: str) -> str:
    color = DENSITY_COLOR.get(density, "#94A3B8")
    return f'<span class="density-badge" style="background:{color};">{density.upper()}</span>'


def lane_status_html(active: bool, seconds: float) -> str:
    """Pill showing whether a lane is currently green (with countdown)
    or waiting at red (with how long it has been waiting) — no emoji."""
    if active:
        return f'<span class="lane-status status-active">ACTIVE · {int(max(seconds,0))}s left</span>'
    return f'<span class="lane-status status-waiting">WAITING · {int(seconds)}s</span>'


def traffic_light_html(state: str) -> str:
    """state: 'red' | 'yellow' | 'green'"""
    red_cls = "tl-dot tl-red-on" if state == "red" else "tl-dot"
    yellow_cls = "tl-dot tl-yellow-on" if state == "yellow" else "tl-dot"
    green_cls = "tl-dot tl-green-on" if state == "green" else "tl-dot"
    return f"""
    <div class="traffic-light">
        <div class="{red_cls}"></div>
        <div class="{yellow_cls}"></div>
        <div class="{green_cls}"></div>
    </div>
    """


def lane_title_html(name: str, subtitle: str = "") -> str:
    sub = f'<div class="lane-sub">{subtitle}</div>' if subtitle else ""
    return f'<div class="lane-name">{name}</div>{sub}'


def lane_card_html(count: int, density: str, status_html: str, green_time: int, light_state: str) -> str:
    """Renders a complete, cleanly styled card for lane metrics and traffic light."""
    tl_html = traffic_light_html(light_state)
    d_badge = density_badge_html(density)
    return f"""
    <div class="up-panel">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px;">
            <div style="flex:1;">
                <div style="font-size:1.65rem; font-weight:800; color:{SLATE_900}; line-height:1.1;">{count}</div>
                <div style="font-size:0.72rem; color:{SLATE_500}; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:2px; margin-bottom:8px;">Vehicles</div>
                <div style="display:flex; flex-direction:column; gap:5px; align-items:flex-start;">
                    {d_badge}
                    {status_html}
                </div>
                <div style="font-size:0.73rem; color:{SLATE_500}; margin-top:8px;">Allocated green: <strong>{green_time}s</strong></div>
            </div>
            <div>
                {tl_html}
            </div>
        </div>
    </div>
    """
