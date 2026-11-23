"""
Root entry point for Streamlit Community Cloud and local execution.
Delegates directly to UrbanPulseProject/app.py.
"""
import os
import sys
import runpy

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.join(ROOT_DIR, "UrbanPulseProject")

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# Switch working directory context to UrbanPulseProject for consistent asset resolution
os.chdir(PROJECT_DIR)

target_app = os.path.join(PROJECT_DIR, "app.py")
runpy.run_path(target_app, run_name="__main__")
