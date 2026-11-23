"""
config.py
---------
Central control panel for the UrbanPulse dashboard.

HOW TO HIDE / REVEAL THE "IMPRESSIVE" FEATURES
------------------------------------------------
Set ADVANCED_MODE = False for your first/early presentation -> the
dashboard shows ONLY the core Live Monitoring screen (clean, simple).

Set ADVANCED_MODE = True for your FINAL presentation -> the SAME
codebase instantly reveals:
    - Analytics tab (vehicle-type breakdown, session stats, CSV export)
    - Prediction tab (24-hour traffic forecast graph)
    - Emergency Vehicle Priority override control

No other file needs to change. Just flip the one line below.
"""

APP_TITLE = "UrbanPulse"
APP_SUBTITLE = "AI-Powered Traffic Intelligence System"

# ============== FLIP THIS ONE LINE ==============
ADVANCED_MODE = True
# =================================================

# Fine-grained control - follows ADVANCED_MODE by default
SHOW_ANALYTICS_TAB = ADVANCED_MODE
SHOW_PREDICTION_TAB = ADVANCED_MODE
SHOW_EMERGENCY_OVERRIDE = ADVANCED_MODE
SHOW_ADVANCED_KPIS = ADVANCED_MODE
