import numpy as np
import pandas as pd


def update_pmu_history(state, row_clean, relay, result):
    """
    Build PMU waveform with smooth motion + disturbance effect
    """

    if "pmu_history" not in state:
        state.pmu_history = []

    # ---------------- Base values ----------------
    va = row_clean[f"{relay}-PM1:V"] / 1000
    vb = row_clean[f"{relay}-PM2:V"] / 1000
    vc = row_clean[f"{relay}-PM3:V"] / 1000

    t = len(state.pmu_history)

    # ---------------- Smooth waveform ----------------
    phase_a = va + 0.6 * np.sin(t / 2)
    phase_b = vb + 0.6 * np.sin(t / 2 + 2)
    phase_c = vc + 0.6 * np.sin(t / 2 + 4)

    # ---------------- ⚡ Attack effect ----------------
    if result["Final_binary"] == 1:
        spike = 3 + result["Final_conf"] * 4
        phase_a += spike * np.sin(t)
        phase_b += spike * np.cos(t)
        phase_c += spike * np.sin(t / 2)

    # ---------------- Save history ----------------
    point = {
        "Phase A": phase_a,
        "Phase B": phase_b,
        "Phase C": phase_c,
    }

    state.pmu_history.append(point)
    state.pmu_history = state.pmu_history[-60:]

    return pd.DataFrame(state.pmu_history)