"""
detection.py
------------
YOLOv8-based real-time vehicle detection module for UrbanPulse.

Uses the pretrained Ultralytics YOLOv8 nano model (trained on COCO),
which recognizes car, motorcycle, bus, and truck classes.
Includes a native pure-PyTorch NMS fallback to guarantee 100% stability
even on platforms with missing or mismatched torchvision C++ extensions.
"""

import os
import sys
import types
import cv2
import torch

# COCO class-id -> vehicle type mapping
VEHICLE_CLASSES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WEIGHTS = os.path.join(BASE_DIR, "yolov8n.pt")

_model = None  # loaded lazily (only once, on first use)


def _pure_pytorch_nms(boxes, scores, iou_threshold=0.5):
    """Pure PyTorch implementation of Non-Maximum Suppression (NMS).
    Guarantees NMS works reliably even when torchvision C++ binary is missing.
    """
    if boxes.numel() == 0:
        return torch.empty((0,), dtype=torch.int64, device=boxes.device)
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort(descending=True)
    keep = []
    while order.numel() > 0:
        i = order[0].item()
        keep.append(i)
        if order.numel() == 1:
            break
        xx1 = torch.maximum(x1[i], x1[order[1:]])
        yy1 = torch.maximum(y1[i], y1[order[1:]])
        xx2 = torch.minimum(x2[i], x2[order[1:]])
        yy2 = torch.minimum(y2[i], y2[order[1:]])
        w = torch.clamp(xx2 - xx1, min=0.0)
        h = torch.clamp(yy2 - yy1, min=0.0)
        inter = w * h
        iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-7)
        idx = (iou <= iou_threshold).nonzero().reshape(-1)
        if idx.numel() == 0:
            break
        order = order[idx + 1]
    return torch.tensor(keep, dtype=torch.int64, device=boxes.device)


def _ensure_torchvision_compatibility():
    """Validates torchvision.ops.nms; installs pure-PyTorch fallback if broken."""
    try:
        import torchvision
        import torchvision.ops
        # Test NMS execution
        test_boxes = torch.tensor([[0.0, 0.0, 10.0, 10.0]], dtype=torch.float32)
        test_scores = torch.tensor([0.9], dtype=torch.float32)
        _ = torchvision.ops.nms(test_boxes, test_scores, 0.5)
    except Exception:
        # Install fallback pure PyTorch implementation
        dummy = types.ModuleType("torchvision")
        ops_mod = types.ModuleType("torchvision.ops")
        setattr(ops_mod, "nms", _pure_pytorch_nms)
        setattr(dummy, "ops", ops_mod)
        sys.modules["torchvision"] = dummy
        sys.modules["torchvision.ops"] = ops_mod


def load_model(weights: str | None = None):
    """Loads (and caches) the YOLOv8 model."""
    global _model
    if weights is None:
        weights = DEFAULT_WEIGHTS if os.path.exists(DEFAULT_WEIGHTS) else "yolov8n.pt"
    if _model is None:
        _ensure_torchvision_compatibility()
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
        preds = model(frame, verbose=False)
        first_res = preds[0] if isinstance(preds, (list, tuple)) else next(iter(preds))
        boxes = getattr(first_res, "boxes", None)
        if boxes is None:
            return []

        detections = []
        for box in boxes:
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
