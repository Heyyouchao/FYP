# engine/scoring.py

def compute_fusion_scores(row, raw_scores):

    scores = {}

    for r in ["R1", "R2", "R3", "R4"]:

        physical = raw_scores.get(r, 0)

        relay_signal = min(row.get(f"relay{r[-1]}_log", 0), 1)

        cyber_signal = min(
            row.get(f"control_panel_log{r[-1]}", 0) +
            row.get(f"snort_log{r[-1]}", 0),
            1
        )

        # -------------------------
        # FUSION LOGIC
        # -------------------------

        # 🔴 cyber + relay → strongest
        if cyber_signal > 0 and relay_signal > 0:
            score = physical + 0.8

        # 🟡 cyber only
        elif cyber_signal > 0:
            score = physical + 0.6

        # 🟢 relay only
        else:
            score = physical + 0.2 * relay_signal

        scores[r] = score

    return scores


def get_most_affected_relay(row, raw_scores):

    scores = compute_fusion_scores(row, raw_scores)

    return max(scores, key=scores.get), scores