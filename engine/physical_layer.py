# ============================================================
# PHYSICAL LAYER ENGINE (FINAL HYBRID: MODEL + RELAY LOG)
# ============================================================

# ------------------------------------------------------------
# COLOR FUNCTION
# ------------------------------------------------------------
def get_color(norm_score):
    if norm_score <= 1.0:
        return "🟢"
    elif norm_score <= 1.4:
        return "🟡"
    else:
        return "🔴"


# ------------------------------------------------------------
# RELAY COLORS (MODEL)
# ------------------------------------------------------------
def get_relay_colors(relay_scores):

    colors = {r: get_color(s) for r, s in relay_scores.items()}

    # limit to top 2 red relays
    red_relays = [r for r, c in colors.items() if c == "🔴"]

    if len(red_relays) > 2:
        sorted_relays = sorted(
            relay_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        top2 = [r for r, _ in sorted_relays[:2]]

        for r in red_relays:
            if r not in top2:
                colors[r] = "🟡"

    return colors


# ------------------------------------------------------------
# LINE COLORS (MODEL)
# ------------------------------------------------------------
def get_line_colors(relay_scores):

    line_scores = {
        "L1": max(relay_scores.get("R1", 0), relay_scores.get("R2", 0)),
        "L2": max(relay_scores.get("R3", 0), relay_scores.get("R4", 0))
    }

    colors = {l: get_color(s) for l, s in line_scores.items()}

    return colors


# ------------------------------------------------------------
# RELAY LOG (DATASET)
# ------------------------------------------------------------
def get_relay_log_from_row(row):

    mapping = {
        "R1": "relay1_log",
        "R2": "relay2_log",
        "R3": "relay3_log",
        "R4": "relay4_log"
    }

    relay_log = {}

    for r, col in mapping.items():

        if col in row:
            val = row[col]

            if val in [1, "TRIP", "Trip", True]:
                relay_log[r] = "TRIP"
            else:
                relay_log[r] = "IDLE"
        else:
            relay_log[r] = "UNKNOWN"

    return relay_log


# ------------------------------------------------------------
# BREAKER (FOLLOWS RELAY LOG)
# ------------------------------------------------------------
def get_breaker_from_relay_log(relay_log):

    breaker = {}

    for i in range(1, 5):
        r = f"R{i}"
        br = f"BR{i}"

        action = relay_log.get(r, "UNKNOWN")

        if action == "TRIP":
            breaker[br] = "🔴"   # OPEN
        elif action == "IDLE":
            breaker[br] = "🟢"   # CLOSED
        else:
            breaker[br] = "⚪"

    return breaker


# ------------------------------------------------------------
# LINE OVERRIDE (BREAKER ONLY AFFECTS WHEN OPEN)
# ------------------------------------------------------------
def override_line_with_breaker(line_colors, breaker):

    final_line = line_colors.copy()

    # L1 → BR1 & BR2
    if breaker.get("BR1") == "🔴" or breaker.get("BR2") == "🔴":
        final_line["L1"] = "🔴"
    else:
        final_line["L1"] = line_colors["L1"]

    # L2 → BR3 & BR4
    if breaker.get("BR3") == "🔴" or breaker.get("BR4") == "🔴":
        final_line["L2"] = "🔴"
    else:
        final_line["L2"] = line_colors["L2"]

    return final_line


# ------------------------------------------------------------
# ENFORCE SINGLE RED LINE
# - only applies when BOTH lines are red
# - breaker is main if open
# ------------------------------------------------------------
def enforce_single_red_line_with_breaker(line_scores, line_colors, breaker):

    # only intervene if BOTH are red
    if not (line_colors["L1"] == "🔴" and line_colors["L2"] == "🔴"):
        return line_colors.copy()

    # breaker priority
    if breaker.get("BR1") == "🔴" or breaker.get("BR2") == "🔴":
        return {"L1": "🔴", "L2": "🟡"}

    if breaker.get("BR3") == "🔴" or breaker.get("BR4") == "🔴":
        return {"L1": "🟡", "L2": "🔴"}

    # fallback → highest relay-score line wins
    max_line = max(line_scores, key=line_scores.get)

    return {
        "L1": "🔴" if max_line == "L1" else "🟡",
        "L2": "🔴" if max_line == "L2" else "🟡"
    }


# ------------------------------------------------------------
# BUS (MODEL)
# ------------------------------------------------------------
def get_bus_colors(relay_scores):

    bus_scores = {
        "B1": relay_scores.get("R1", 0),
        "B2": (relay_scores.get("R2", 0) + relay_scores.get("R3", 0)) / 2,
        "B3": relay_scores.get("R4", 0)
    }

    return {b: get_color(s) for b, s in bus_scores.items()}, bus_scores


# ------------------------------------------------------------
# GENERATOR (FOLLOWS FINAL LINE)
# ------------------------------------------------------------
def get_generator_colors(line_status):

    return {
        "G1": line_status["L1"],
        "G2": line_status["L2"]
    }


# ------------------------------------------------------------
# ATTACH RELAY INFO (MODEL + DATASET + EXPLAINABILITY)
# ------------------------------------------------------------
def attach_relay_info(physical_layer, top_features, relay_log):

    for r in physical_layer["relay"]:

        physical_layer["relay"][r] = {
            "color": physical_layer["relay"][r],
            "action": relay_log.get(r, "UNKNOWN"),
            "top_features": top_features.get(r, [])
        }

    return physical_layer


# ------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------
def process_event(relay_scores, row, top_features):

    # 1. MODEL → relay disturbance
    relay_colors = get_relay_colors(relay_scores)

    # 2. DATASET → relay command
    relay_log = get_relay_log_from_row(row)

    # 3. BREAKER → execution
    breaker = get_breaker_from_relay_log(relay_log)

    # 4. MODEL → predicted line (untouched)
    model_line = get_line_colors(relay_scores)

    # 5. REAL → breaker override
    final_line = override_line_with_breaker(model_line, breaker)

    # 6. line scores for tie-break only
    line_scores = {
        "L1": max(relay_scores.get("R1", 0), relay_scores.get("R2", 0)),
        "L2": max(relay_scores.get("R3", 0), relay_scores.get("R4", 0))
    }

    # 7. enforce single red only if both are red
    final_line = enforce_single_red_line_with_breaker(
        line_scores,
        final_line,
        breaker
    )

    # 8. BUS
    bus, bus_scores = get_bus_colors(relay_scores)

    # 9. GENERATOR follows FINAL line
    generator = get_generator_colors(final_line)

    # 10. COMBINE
    physical_layer = {
        "relay": relay_colors,
        "breaker": breaker,
        "line": final_line,
        "line_model": model_line,   # keep for mismatch checking
        "bus": bus,
        "generator": generator,
        "relay_log": relay_log
    }

    # 11. attach explainability
    physical_layer = attach_relay_info(
        physical_layer,
        top_features,
        relay_log
    )

    return physical_layer