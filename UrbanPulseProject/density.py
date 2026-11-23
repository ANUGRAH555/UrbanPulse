"""
density.py
----------
Traffic density estimation for UrbanPulse.

Design choice: each lane has its OWN dedicated video source (its own
camera or its own uploaded clip), so density for a lane = number of
vehicles detected in THAT lane's frame. No cross-lane ROI splitting is
needed (that would only be required if a single wide-angle camera
covered all lanes at once).

Classification uses two configurable thresholds T1 / T2:
    count <  T1        -> Low
    T1 <= count < T2    -> Medium
    count >= T2         -> High
"""

T1 = 5   # Low / Medium boundary
T2 = 10  # Medium / High boundary


def count_vehicles(detections):
    """Simple count of all detected vehicles in a frame."""
    if not detections:
        return 0
    return len(detections)


def classify_density(count: int) -> str:
    if count < T1:
        return "Low"
    elif count < T2:
        return "Medium"
    else:
        return "High"


def get_lane_status(detections):
    """Convenience wrapper: returns (count, density_label) for one lane."""
    count = count_vehicles(detections)
    density = classify_density(count)
    return count, density
