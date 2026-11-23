"""
detection.py
------------
YOLOv8-based real-time vehicle detection module for UrbanPulse.

Uses the pretrained Ultralytics YOLOv8 nano model (trained on COCO),
which already recognizes car / motorcycle / bus / truck classes,
so NO custom training is required for the prototype.
"""

import os
import cv2

# COCO class-id -> vehicle type mapping
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WEIGHTS = os.path.join(BASE_DIR, "yolov8n.pt")

_model = None  # loaded lazily (only once, on first use)


def load_model(weights: str = None):
    """Loads (and caches) the YOLOv8 model."""
    global _model
    if weights is None:
        weights = DEFAULT_WEIGHTS if os.path.exists(DEFAULT_WEIGHTS) else "yolov8n.pt"
    if _model is None:
        import sys
        import types
        try:
            import torchvision
            import torchvision.ops
        except Exception:
            if "torchvision" not in sys.modules or not hasattr(sys.modules.get("torchvision"), "ops"):
                dummy = types.ModuleType("torchvision")
                sys.modules["torchvision"] = dummy
        from ultralytics import YOLO
        _model = YOLO(weights)
    return _model


def detect_vehicles(frame, conf_threshold: float = 0.35):
    """
    Runs YOLOv8 inference on a single frame.

    Returns a list of dicts:
        {"class": "car", "bbox": (x1,y1,x2,y2), "conf": 0.87, "center": (cx,cy)}
    """
    if frame is None or not hasattr(frame, "shape") or frame.size == 0:
        return []

    try:
        model = load_model()
        results = model(frame, verbose=False)[0]

        detections = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            if cls_id in VEHICLE_CLASSES and conf >= conf_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                detections.append({
                    "class": VEHICLE_CLASSES[cls_id],
                    "bbox": (x1, y1, x2, y2),
                    "conf": conf,
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                })
        return detections
    except Exception as e:
        print(f"Vehicle detection warning: {e}")
        return []


def draw_detections(frame, detections):
    """Draws bounding boxes + labels on the frame (for display in the dashboard)."""
    if frame is None or not hasattr(frame, "shape") or frame.size == 0:
        return frame

    colors = {
        "car": (0, 255, 0),
        "bus": (255, 140, 0),
        "truck": (0, 0, 255),
        "motorcycle": (255, 0, 255),
    }
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        color = colors.get(det["class"], (255, 255, 255))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label = f"{det['class']} {det['conf']:.2f}"
        cv2.putText(frame, label, (x1, max(y1 - 8, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame
