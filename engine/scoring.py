# engine/scoring.py

def compute_fusion_scores(row, raw_scores):
    scores = {}

    for r in ["R1", "R2", "R3", "R4"]:
        idx = r[-1]

        physical = raw_scores.get(r, 0)

        relay_signal = min(row.get(f"relay{idx}_log", 0), 1)

        cyber_signal = min(
            row.get(f"control_panel_log{idx}", 0) +
            row.get(f"snort_log{idx}", 0),
            1
        )

        z_signal = min(row.get(f"R{idx}-PA:Z_inf_flag", 0), 1)

        # Base score starts from physical evidence
        score = physical

        # Strong physical anomaly boost
        if z_signal > 0:
            score += 0.5

        # Operational / cyber evidence
        if cyber_signal > 0 and relay_signal > 0:
            score += 0.8
        elif cyber_signal > 0:
            score += 0.6
        elif relay_signal > 0:
            score += 0.2

        scores[r] = score

    return scores


def get_most_affected_relay(row, raw_scores):

    scores = compute_fusion_scores(row, raw_scores)

    return max(scores, key=scores.get), scores