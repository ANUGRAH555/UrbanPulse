"""
video_source.py
----------------
Unified video input handling for UrbanPulse.

Supports TWO input types with the exact same downstream code:
  - "live"   -> webcam index (0,1,...) or an RTSP/HTTP camera URL
  - "upload" -> a local video file path (e.g. an uploaded .mp4)

Also includes generate_demo_video(), which creates a synthetic traffic
clip (moving colored blocks on a road) with OpenCV for pipeline testing.
"""

import os
import random
import cv2
import numpy as np


def get_video_source(source_type: str, source_path):
    """
    source_type: 'live' or 'upload'
    source_path: camera index/URL (live) OR file path (upload)
    """
    try:
        cap = cv2.VideoCapture(source_path)
        return cap
    except Exception as e:
        print(f"Video source error for {source_path}: {e}")
        return None


def read_frame_loop(cap):
    """Reads one frame; if the video has ended, rewinds to the start
    (so uploaded clips loop forever during a live demo)."""
    if cap is None or not cap.isOpened():
        return False, None
    try:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
        return ret, frame
    except Exception as e:
        print(f"Frame read error: {e}")
        return False, None


def generate_demo_video(path: str, density: str = "medium", duration_sec: int = 15,
                         fps: int = 15, width: int = 640, height: int = 480) -> str:
    """Generates a synthetic traffic clip for pipeline/UI testing."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    density_map = {"low": 3, "medium": 8, "high": 15}
    n_vehicles = density_map.get(str(density).lower(), 8)

    # Cross-platform video codec selection
    codecs = ["mp4v", "avc1", "MJPG"]
    out = None
    for codec in codecs:
        try:
            fourcc = cv2.VideoWriter_fourcc(*codec)
            writer = cv2.VideoWriter(path, fourcc, fps, (width, height))
            if writer.isOpened():
                out = writer
                break
        except Exception:
            continue

    if out is None or not out.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(path, fourcc, fps, (width, height))

    colors = [(0, 255, 0), (255, 140, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255)]
    vehicles = []
    for _ in range(n_vehicles):
        vehicles.append({
            "x": random.randint(0, width),
            "y": random.randint(60, height - 60),
            "w": random.randint(30, 60),
            "h": random.randint(20, 35),
            "speed": random.randint(2, 6),
            "color": random.choice(colors),
        })

    total_frames = duration_sec * fps
    for _ in range(total_frames):
        frame = np.full((height, width, 3), (60, 60, 60), dtype=np.uint8)
        for lx in range(0, width, 40):
            cv2.line(frame, (lx, height // 2), (lx + 20, height // 2), (255, 255, 255), 2)

        for v in vehicles:
            v["x"] += v["speed"]
            if v["x"] > width:
                v["x"] = -v["w"]
            cv2.rectangle(frame, (v["x"], v["y"]), (v["x"] + v["w"], v["y"] + v["h"]), v["color"], -1)

        out.write(frame)
    out.release()
    return path


def ensure_demo_videos(data_dir: str):
    """Creates 4 demo videos (one per lane, mixed densities) if missing."""
    os.makedirs(data_dir, exist_ok=True)
    presets = [("lane1_demo.mp4", "low"), ("lane2_demo.mp4", "high"),
               ("lane3_demo.mp4", "medium"), ("lane4_demo.mp4", "medium")]
    paths = []
    for filename, density in presets:
        full_path = os.path.join(data_dir, filename)
        if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
            generate_demo_video(full_path, density=density)
        paths.append(full_path)
    return paths
