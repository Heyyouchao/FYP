def get_relay_flow(relay):
    affect = "L1" if relay in ["R1", "R2"] else "L2"

    affected_by = {
        "R1": "B1",
        "R2": "B2",
        "R3": "B2",
        "R4": "B3"
    }

    return {
        "affected_by": affected_by.get(relay),
        "affects_on": affect
    }


def get_breaker_flow(breaker):
    relay_map = {
        "BR1": "R1", "BR2": "R2",
        "BR3": "R3", "BR4": "R4"
    }

    line_map = {
        "BR1": "L1", "BR2": "L1",
        "BR3": "L2", "BR4": "L2"
    }

    return {
        "affected_by": relay_map.get(breaker),
        "affects_on": line_map.get(breaker)
    }


def get_line_flow(line):
    if line == "L1":
        return {
            "affected_by": "BR1, BR2",
            "affects_on": "B1, B2"
        }
    else:
        return {
            "affected_by": "BR3, BR4",
            "affects_on": "B2, B3"
        }


def get_bus_flow(bus):
    mapping = {
        "B1": ("L1", "G1"),
        "B2": ("L1, L2", "—"),
        "B3": ("L2", "G2")
    }

    a, b = mapping.get(bus, ("—", "—"))

    return {
        "affected_by": a,
        "affects_on": b
    }


def get_generator_flow(gen):
    mapping = {
        "G1": ("B1", "—"),
        "G2": ("B3", "—")
    }

    a, b = mapping.get(gen, ("—", "—"))

    return {
        "affected_by": a,
        "affects_on": b
    }


def get_cyber_logs(row, relay):
    logs = []

    relay_num = relay.replace("R", "")

    control_col = f"control_panel_log{relay_num}"
    snort_col = f"snort_log{relay_num}"

    if control_col in row and row[control_col] == 1:
        logs.append("Control Panel Activity")

    if snort_col in row and row[snort_col] == 1:
        logs.append("🚨 Snort Alert")

    if not logs:
        logs.append("No cyber activity")

    return logs