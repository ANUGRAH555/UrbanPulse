# UrbanPulse — AI Traffic Intelligence Platform

UrbanPulse is an AI-powered traffic intelligence system that replaces fixed-timer traffic signals with a real-time, data-driven adaptive control system.

Live vehicle detection, lane-wise density estimation, and priority-based adaptive signal control running on live camera feeds or uploaded video footage.

---

## 🌟 Key Features

- **Live Multi-Lane Monitoring**: Real-time video processing across 4 independent intersection lanes.
- **YOLOv8 Real-Time Vehicle Detection**: Pretrained COCO model recognizing cars, buses, trucks, and motorcycles with bounding box visual overlays.
- **Dynamic Density Classification**: Real-time traffic density classification (Low, Medium, High).
- **Adaptive Signal Control**: Dynamically distributes green light cycle times based on traffic weights with safety limits ($10\text{s} \le \text{green} \le 60\text{s}$).
- **Priority + Aging Scheduler**: Prevents starvation by rewarding waiting lanes with aging priority points over time.
- **Emergency Vehicle Priority Override**: Instantly grants maximum green light to cleared lanes with ambulances or emergency vehicles.
- **Traffic Forecasting**: Scikit-Learn Random Forest model for quick predictions and 24-hour traffic volume forecasts.
- **Analytics & Reporting**: Vehicle distribution breakdown, session statistics, and one-click CSV report export.
- **Modern SaaS Dashboard**: Clean, responsive layout with traffic light visualizers, live KPI cards, and interactive charts.

---

## 🚀 Quick Start (Local)

### 1. Clone the repository
```bash
git clone https://github.com/ANUGRAH555/UrbanPulse.git
cd UrbanPulse
```

### 2. Set up virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit dashboard
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

---

## ☁️ Streamlit Community Cloud Deployment

This repository is pre-configured and fully compatible with **Streamlit Community Cloud**:
- **Main file path**: `app.py`
- **Python requirements**: `requirements.txt` (uses `opencv-python-headless` for cloud compatibility)
- **Linux system dependencies**: `packages.txt` (`libgl1`, `libglib2.0-0`)
- **Theme & server config**: `.streamlit/config.toml`

---

## 📂 Project Architecture

```
UrbanPulse/
├── app.py                     # Root application entry point for Streamlit
├── requirements.txt           # Python dependencies
├── packages.txt               # OS system packages for Streamlit Cloud
├── .gitignore                 # Excludes temp video files, cache, and envs
├── .streamlit/
│   └── config.toml            # SaaS theme and server settings
├── UrbanPulseProject/
│   ├── app.py                 # Core dashboard application
│   ├── config.py              # Configuration & feature switches
│   ├── visuals.py             # UI design system & HTML components
│   ├── detection.py           # YOLOv8 vehicle detection pipeline
│   ├── density.py             # Lane density classification logic
│   ├── signal_control.py      # Adaptive signal timing & lane scheduler
│   ├── prediction.py          # Random Forest traffic flow forecaster
│   ├── video_source.py        # Video stream handling & demo clips
│   ├── benchmark.py           # Comparative benchmark vs fixed-cycle
│   ├── yolov8n.pt             # Pretrained YOLOv8 nano model
│   ├── data/                  # Historical data & demo clips
│   └── temp/                  # Session uploads (tracked via .gitkeep)
└── README.md
```

---

## 🧪 Benchmark Testing

Run the comparative offline benchmark:
```bash
python UrbanPulseProject/benchmark.py
```
Outputs performance statistics and generates `benchmark_result.png`.

---

## 📄 License
MIT License
