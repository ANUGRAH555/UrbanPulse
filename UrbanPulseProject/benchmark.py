"""
benchmark.py
------------
Quick, offline benchmark comparing the Adaptive Signal Control algorithm
against a plain Fixed-Cycle baseline, using simulated lane density data.

Run this and paste the printed numbers/graph into your report's
"Expected Outcomes" / "Testing and Validation" chapter.

    python benchmark.py
"""

import os
import sys
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from signal_control import calculate_green_times, fixed_cycle_baseline, TOTAL_CYCLE

LANES = ["lane_1", "lane_2", "lane_3", "lane_4"]
DENSITY_LEVELS = ["Low", "Medium", "High"]


def estimate_wait_time(count, green_time):
    if green_time <= 0:
        return count * 5
    return max(0, (count * 3) - (green_time * 0.4))


def run_benchmark(n_cycles=50):
    adaptive_waits, fixed_waits = [], []

    for _ in range(n_cycles):
        counts = {lane: random.randint(0, 18) for lane in LANES}
        densities = {}
        for lane, c in counts.items():
            if c < 5:
                densities[lane] = "Low"
            elif c < 10:
                densities[lane] = "Medium"
            else:
                densities[lane] = "High"

        adaptive_green = calculate_green_times(densities)
        fixed_green = fixed_cycle_baseline(LANES)

        adaptive_wait = sum(estimate_wait_time(counts[l], adaptive_green[l]) for l in LANES)
        fixed_wait = sum(estimate_wait_time(counts[l], fixed_green[l]) for l in LANES)

        adaptive_waits.append(adaptive_wait)
        fixed_waits.append(fixed_wait)

    avg_adaptive = sum(adaptive_waits) / max(len(adaptive_waits), 1)
    avg_fixed = sum(fixed_waits) / max(len(fixed_waits), 1)
    improvement = (avg_fixed - avg_adaptive) / avg_fixed * 100 if avg_fixed else 0

    print(f"Average wait time (Fixed-Cycle) : {avg_fixed:.2f}")
    print(f"Average wait time (Adaptive)    : {avg_adaptive:.2f}")
    print(f"Improvement                     : {improvement:.1f}%")

    plt.figure(figsize=(8, 4))
    plt.plot(fixed_waits, label="Fixed-Cycle")
    plt.plot(adaptive_waits, label="Adaptive (UrbanPulse)")
    plt.xlabel("Cycle #")
    plt.ylabel("Estimated total wait time")
    plt.title("Adaptive vs Fixed-Cycle Signal Control")
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "benchmark_result.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Saved chart -> {out_path}")


if __name__ == "__main__":
    run_benchmark()
