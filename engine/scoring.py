# engine/scoring.py

def compute_fusion_scores(row, relay_disturbance):

    scores = {}

    for r in ["R1", "R2", "R3", "R4"]:

        physical = relay_disturbance.get(r, 0)

        relay_log = row.get(f"relay{r[-1]}_log", 0)

        cyber = (
            row.get(f"control_panel_log{r[-1]}", 0) +
            row.get(f"snort_log{r[-1]}", 0)
        )

        # 🔥 fusion (clean + balanced)
        scores[r] = physical + relay_log*0.5 + cyber*0.5

    return scores


def get_most_affected_relay(row, relay_disturbance):

    scores = compute_fusion_scores(row, relay_disturbance)

    return max(scores, key=scores.get), scores