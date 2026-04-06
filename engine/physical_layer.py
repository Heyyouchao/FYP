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
# LINE OVERRIDE (REAL SYSTEM BEHAVIOR)
# ------------------------------------------------------------
def override_line_with_breaker(line_colors, breaker):

    final_line = line_colors.copy()

    # L1 → BR1 & BR2
    if breaker.get("BR1") == "🔴" or breaker.get("BR2") == "🔴":
        final_line["L1"] = "🔴"

    # L2 → BR3 & BR4
    if breaker.get("BR3") == "🔴" or breaker.get("BR4") == "🔴":
        final_line["L2"] = "🔴"

    return final_line

def enforce_single_red_line_with_breaker(line_scores, line_colors, breaker):

    red_lines = [l for l, c in line_colors.items() if c == "🔴"]

    if len(red_lines) <= 1:
        return line_colors

    # -------------------------
    # 🔥 Priority 1: breaker-based line
    # -------------------------
    breaker_line = None

    if breaker["BR1"] == "🔴" or breaker["BR2"] == "🔴":
        breaker_line = "L1"

    if breaker["BR3"] == "🔴" or breaker["BR4"] == "🔴":
        # if both sides have breaker → choose stronger later
        if breaker_line is None:
            breaker_line = "L2"

    # -------------------------
    # 🔥 If breaker decides
    # -------------------------
    if breaker_line:
        for l in red_lines:
            if l != breaker_line:
                line_colors[l] = "🟡"
        return line_colors

    # -------------------------
    # 🔥 Fallback: highest score
    # -------------------------
    max_line = max(line_scores, key=line_scores.get)

    for l in red_lines:
        if l != max_line:
            line_colors[l] = "🟡"

    return line_colors


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
# GENERATOR (FROM BUS)
# ------------------------------------------------------------
def get_generator_colors(bus_scores):

    generator_scores = {
        "G1": bus_scores.get("B1", 0),
        "G2": bus_scores.get("B3", 0)
    }

    return {g: get_color(s) for g, s in generator_scores.items()}


# ------------------------------------------------------------
# ATTACH RELAY INFO (MODEL + DATASET + EXPLAINABILITY)
# ------------------------------------------------------------
def attach_relay_info(physical_layer, top_features, relay_log):

    for r in physical_layer["relay"]:

        physical_layer["relay"][r] = {
            "color": physical_layer["relay"][r],            # model
            "action": relay_log.get(r, "UNKNOWN"),          # dataset
            "top_features": top_features.get(r, [])         # explainability
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

    # 4. MODEL → predicted line
    model_line = get_line_colors(relay_scores)

    # 5. REAL → override by breaker
    final_line = override_line_with_breaker(model_line, breaker)

    # 🔥 6. Enforce single dominant line
    line_scores = {
        "L1": max(relay_scores.get("R1", 0), relay_scores.get("R2", 0)),
        "L2": max(relay_scores.get("R3", 0), relay_scores.get("R4", 0))
    }

    final_line = enforce_single_red_line_with_breaker(
        line_scores,
        final_line,
        breaker
    )

    # 6. BUS
    bus, bus_scores = get_bus_colors(relay_scores)

    # 7. GENERATOR
    generator = get_generator_colors(bus_scores)

    # 8. COMBINE
    physical_layer = {
        "relay": relay_colors,
        "breaker": breaker,
        "line": final_line,
        "line_model": model_line,   # 🔥 important for mismatch
        "bus": bus,
        "generator": generator,
        "relay_log": relay_log      # 🔥 useful later
    }

    # 9. attach explainability
    physical_layer = attach_relay_info(
        physical_layer,
        top_features,
        relay_log
    )

    return physical_layer