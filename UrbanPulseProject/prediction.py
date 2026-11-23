"""
prediction.py
-------------
Short-term traffic flow prediction for UrbanPulse using a Random Forest
model trained on historical traffic data stored in a plain CSV file.

If data/historical_traffic.csv doesn't exist yet, it is generated
automatically the first time this module is used, using a realistic
daily traffic pattern (morning + evening peaks, lighter weekends).
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "historical_traffic.csv")

_model = None


def generate_synthetic_data(save: bool = True) -> pd.DataFrame:
    """Creates a realistic-looking synthetic traffic dataset."""
    hours = np.arange(0, 24, 0.25)
    days = np.arange(0, 7)  # 0=Mon ... 6=Sun
    rows = []
    for day in days:
        weekend_factor = 0.6 if day >= 5 else 1.0
        for hour in hours:
            # two peaks: ~9am and ~6pm
            morning_peak = 10 * np.exp(-((hour - 9) ** 2) / 4)
            evening_peak = 12 * np.exp(-((hour - 18) ** 2) / 5)
            base = 4 + morning_peak + evening_peak
            noise = np.random.normal(0, 1.5)
            count = max(0, (base * weekend_factor) + noise)
            rows.append({"day": int(day), "hour": float(hour), "count": round(count)})

    df = pd.DataFrame(rows)
    if save:
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        df.to_csv(CSV_PATH, index=False)
    return df


def load_data() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        return generate_synthetic_data()
    try:
        df = pd.read_csv(CSV_PATH)
        if df.empty or "day" not in df.columns or "hour" not in df.columns or "count" not in df.columns:
            return generate_synthetic_data()
        return df
    except Exception:
        return generate_synthetic_data()


def train_model():
    global _model
    df = load_data()
    X = df[["day", "hour"]]
    y = df["count"]
    _model = RandomForestRegressor(n_estimators=100, random_state=42)
    _model.fit(X, y)
    return _model


def get_model():
    global _model
    if _model is None:
        train_model()
    return _model


def predict_next(day: int, hour: float):
    """
    day: 0=Monday ... 6=Sunday
    hour: 0-23.75 (e.g., 9.5 = 9:30 AM)

    Returns (predicted_count, density_label)
    """
    try:
        model = get_model()
        day_val = int(day) % 7
        hour_val = float(max(0.0, min(23.75, float(hour))))
        X_input = pd.DataFrame({"day": [day_val], "hour": [hour_val]})
        pred = float(model.predict(X_input)[0])
        pred = max(0.0, pred)

        if pred < 5:
            level = "Low"
        elif pred < 10:
            level = "Medium"
        else:
            level = "High"
        return round(pred, 1), level
    except Exception as e:
        print(f"Prediction warning: {e}")
        return 5.0, "Medium"


def forecast_day(day: int):
    """
    Full 24-hour forecast for a given day (used by the Prediction tab's
    24-hour graph). Returns (hours_list, predicted_counts_list).
    """
    try:
        model = get_model()
        day_val = int(day) % 7
        hours = list(np.arange(0, 24, 0.5))
        X = pd.DataFrame({"day": [day_val] * len(hours), "hour": hours})
        preds = model.predict(X)
        return hours, [round(max(0.0, float(p)), 1) for p in preds]
    except Exception as e:
        print(f"Forecast warning: {e}")
        hours = list(np.arange(0, 24, 0.5))
        return hours, [5.0] * len(hours)
