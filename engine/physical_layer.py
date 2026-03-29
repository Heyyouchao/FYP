# ============================================================
# PHYSICAL LAYER ENGINE (GAR + TOPOLOGY)
# ============================================================

# ------------------------------------------------------------
# COLOR FUNCTION
# ------------------------------------------------------------
def get_color(score):
    if score < 0.15:
        return "🟢"
    elif score < 0.20:
        return "🟡"
    else:
        return "🔴"


# ------------------------------------------------------------
# RELAY COLORS
# ------------------------------------------------------------
def get_relay_colors(relay_scores):

    colors = {r: get_color(s) for r, s in relay_scores.items()}

    red_relays = [r for r, c in colors.items() if c == "🔴"]

    # limit to top 2 red
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
# LINE COLORS
# ------------------------------------------------------------
def get_line_colors(relay_scores):

    line_scores = {
        "L1": max(relay_scores["R1"], relay_scores["R2"]),
        "L2": max(relay_scores["R3"], relay_scores["R4"])
    }

    colors = {l: get_color(s) for l, s in line_scores.items()}

    red_lines = [l for l, c in colors.items() if c == "🔴"]

    # only one red line
    if len(red_lines) > 1:
        max_line = max(line_scores, key=line_scores.get)

        for l in red_lines:
            if l != max_line:
                colors[l] = "🟡"

    return colors


# ------------------------------------------------------------
# BUS COLORS (improved version)
# ------------------------------------------------------------
def get_bus_colors(relay_scores):

    bus_scores = {
        "B1": relay_scores["R1"],
        "B2": (relay_scores["R2"] + relay_scores["R3"]) / 2,  # smoother
        "B3": relay_scores["R4"]
    }

    colors = {b: get_color(s) for b, s in bus_scores.items()}

    red_bus = [b for b, c in colors.items() if c == "🔴"]

    # only one red bus
    if len(red_bus) > 1:
        max_bus = max(bus_scores, key=bus_scores.get)

        for b in red_bus:
            if b != max_bus:
                colors[b] = "🟡"

    return colors


# ------------------------------------------------------------
# GENERATOR COLORS (based on bus)
# ------------------------------------------------------------
def get_generator_colors(bus_scores):

    generator_scores = {
        "G1": bus_scores["B1"],
        "G2": bus_scores["B3"]
    }

    colors = {g: get_color(s) for g, s in generator_scores.items()}

    red_gen = [g for g, c in colors.items() if c == "🔴"]

    if len(red_gen) > 1:
        max_gen = max(generator_scores, key=generator_scores.get)

        for g in red_gen:
            if g != max_gen:
                colors[g] = "🟡"

    return colors


# ------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------
def process_event(relay_scores):

    relay_colors = get_relay_colors(relay_scores)

    line_colors = get_line_colors(relay_scores)

    bus_scores = {
        "B1": relay_scores["R1"],
        "B2": (relay_scores["R2"] + relay_scores["R3"]) / 2,
        "B3": relay_scores["R4"]
    }

    bus_colors = get_bus_colors(relay_scores)

    generator_colors = get_generator_colors(bus_scores)

    return {
        "relay": relay_colors,
        "line": line_colors,
        "bus": bus_colors,
        "gen": generator_colors
    }