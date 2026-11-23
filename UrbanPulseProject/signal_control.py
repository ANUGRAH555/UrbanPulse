"""
signal_control.py
------------------
Adaptive Signal Control algorithm for UrbanPulse.

Core idea: each lane gets a WEIGHT based on its density level.
The total cycle time is then distributed across lanes in proportion
to their weights, subject to MIN_GREEN / MAX_GREEN safety limits so
that no lane is ever starved or allowed to monopolise the cycle.
"""

WEIGHTS = {"Low": 1, "Medium": 2, "High": 3}

MIN_GREEN = 10     # seconds - every lane gets at least this much
MAX_GREEN = 60     # seconds - no lane gets more than this
TOTAL_CYCLE = 120  # seconds - total cycle time shared across all lanes


def calculate_green_times(density_dict: dict) -> dict:
    """
    density_dict: {"lane_1": "Low", "lane_2": "High", ...}
    returns:      {"lane_1": 15, "lane_2": 63, ...}  (seconds)
    """
    if not density_dict:
        return {}
    weights = {lane: WEIGHTS.get(str(d).capitalize(), 1) for lane, d in density_dict.items()}
    total_weight = sum(weights.values()) or 1

    green_times = {}
    for lane, w in weights.items():
        raw_time = (w / total_weight) * TOTAL_CYCLE
        green_times[lane] = int(max(MIN_GREEN, min(MAX_GREEN, round(raw_time))))
    return green_times


def fixed_cycle_baseline(lanes) -> dict:
    """
    A plain fixed-timer baseline (equal green time for every lane),
    used only for benchmarking comparison against the adaptive system.
    """
    if not lanes:
        return {}
    equal_time = TOTAL_CYCLE // max(len(lanes), 1)
    return {lane: equal_time for lane in lanes}


def apply_emergency_override(green_times: dict, emergency_lane: str) -> dict:
    """
    Emergency Vehicle Priority: if an ambulance/fire-truck is flagged on a
    lane, that lane is immediately given the maximum green duration and
    every other lane is dropped to the minimum, so the emergency vehicle
    can clear the intersection as fast as possible.
    """
    if not emergency_lane or emergency_lane == "None" or emergency_lane not in green_times:
        return green_times
    overridden = {}
    for lane in green_times:
        overridden[lane] = MAX_GREEN if lane == emergency_lane else MIN_GREEN
    return overridden


# =========================================================================
# PRIORITY + AGING LANE SCHEDULER
# =========================================================================
PRIORITY_WEIGHTS = {"Low": 1, "Medium": 3, "High": 6}
AGING_RATE = 0.6  # priority points gained per second a lane waits at red


def select_next_lane(densities: dict, wait_times: dict, exclude_lane: str = None) -> str:
    """
    Chooses which lane should get the green signal next.

    densities:    {"lane_1": "Low", ...}            - current density per lane
    wait_times:   {"lane_1": 12.4, ...}              - seconds each lane has waited at red
    exclude_lane: don't let the lane that just finished repeat immediately,
                  UNLESS every other lane is completely empty (Low, 0 wait) -
                  in that case repeating is fine since nothing else needs the signal.
    """
    if not densities:
        return exclude_lane or "lane_1"

    candidates = densities
    if exclude_lane and len(densities) > 1:
        others = {l: d for l, d in densities.items() if l != exclude_lane}
        if others:
            candidates = others

    scores = {
        lane: PRIORITY_WEIGHTS.get(str(density).capitalize(), 1) + float(wait_times.get(lane, 0.0)) * AGING_RATE
        for lane, density in candidates.items()
    }
    if not scores:
        return exclude_lane or list(densities.keys())[0]
    return max(scores, key=scores.get)
