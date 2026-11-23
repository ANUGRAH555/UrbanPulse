# UrbanPulse Pro — AI Traffic Intelligence Platform

Same features as the original UrbanPulse project, with a completely
redesigned, modern SaaS-style dashboard UI: a navbar, a hero banner,
polished card-based layout, and no emoji glyphs anywhere. No database
is used — all data lives in-memory (`st.session_state`) for the session.

This is a **separate folder** from the original `UrbanPulse` project so
the two don't overlap — you can keep both and run whichever you prefer.

## 1. Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

The first time YOLOv8 runs it auto-downloads the pretrained `yolov8n.pt`
weights (a few MB) — needs internet once. If you already have a
`yolov8n.pt` file from the original project, just copy it into this
folder (next to `app.py`) to skip re-downloading.

## 2. Run the dashboard

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

## 3. What changed vs. the original UrbanPulse

- **New visual design**: navbar with a live/idle status pill, a gradient
  hero banner, Inter typeface, indigo accent color, card-based KPI tiles
  with colored accent bars, rounded video previews, pill-style status
  badges — all built to look like a real product dashboard, not a
  script.
- **No emojis anywhere** — every icon-like element is a small CSS shape,
  colored dot, or accent bar instead.
- **Same functionality, same files structure** (`detection.py`,
  `density.py`, `signal_control.py`, `prediction.py`, `video_source.py`,
  `benchmark.py`, `config.py` are unchanged from the original project).

## 4. ⭐ Controlling how much of the project is shown

Open **`config.py`** — one line controls the "impressive extra" features:

```python
ADVANCED_MODE = False   # simple/clean demo (core pipeline only)
ADVANCED_MODE = True    # reveals Analytics tab, 24-hour Prediction tab,
                         # and Emergency Vehicle Priority override
```

## 5. Lane scheduling — Priority + Aging

The lane that turns green next is chosen by a priority score:

```
score(lane) = density_weight(lane) + seconds_waited(lane) * AGING_RATE
```

A busier lane is more likely to be picked next, while the aging term
guarantees a lane waiting a long time will always eventually get its
turn (no lane is ever starved). Each lane card shows a clear status
pill — `ACTIVE · Xs left` or `WAITING · Xs`.

## 6. Real detection vs. placeholder video

For actual vehicle detection to work, use a **real traffic video** —
either your webcam pointed at a real road, or an uploaded real traffic
clip. If no file is uploaded, a placeholder demo clip (moving colored
shapes) is used just so the pipeline doesn't crash — but YOLOv8 won't
recognize those shapes as vehicles, so counts will read near-zero. This
is expected.

## 7. Benchmark (for your report's Testing/Results chapter)

```bash
python benchmark.py
```

## 8. Project structure

```
UrbanPulse_Pro/
├── app.py                 → Streamlit dashboard (new design)
├── config.py                → ADVANCED_MODE feature-flag switch
├── visuals.py                → new design system (navbar, hero, cards, no emoji)
├── detection.py               → YOLOv8 vehicle detection
├── density.py                  → lane density classification (Low/Medium/High)
├── signal_control.py            → adaptive green-time algorithm + emergency override
├── prediction.py                 → Random Forest forecasting (single point + 24-hr)
├── video_source.py                → live camera / upload handling + demo clip generator
├── benchmark.py                    → fixed-cycle vs adaptive comparison script
├── .streamlit/config.toml           → light SaaS theme (indigo accent)
├── data/                              → historical_traffic.csv (auto-generated), demo clips
├── temp/                               → uploaded video files saved here at runtime
└── requirements.txt
```
