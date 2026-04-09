import plotly.graph_objects as go
import streamlit as st

def draw_grid(physical_layer, selected=None):

    RELAY_TO_LINE = {
        "R1": "L1",
        "R2": "L1",
        "R3": "L2",
        "R4": "L2"
    }
    
    relay = physical_layer["relay"]
    generator = physical_layer["generator"]
    bus = physical_layer["bus"]
    breaker = physical_layer["breaker"]
    line_status = physical_layer["line"]
    line_model = physical_layer.get("line_model", {})

    control = st.session_state.get("control_state", {})

    color_map = {
        "🔴": "#ef4444",
        "🟡": "#f59e0b",
        "🟢": "#10b981",
        "⚪": "#9ca3af",
        "🟣": "#8b5cf6"
    }

    HIGHLIGHT_COLOR = "#3b82f6"
    HIGHLIGHT_OPACITY = 0.25
    LINE_HIGHLIGHT_COLOR = "#22d3ee"

    theme = st.get_option("theme.base")

    if theme == "dark":
        font_color = "#e5e7eb"
        line_base_color = "#FFFFFF"
        bus_color = "#94a3b8"
    else:
        font_color = "#111827"
        line_base_color = "#1f2937"
        bus_color = "#64748b"

    fig = go.Figure()

    MAIN_Y = 6.5
    BUS_TOP, BUS_BOTTOM = 7, 4.5
    RELAY_Y = 5.6

    pos = {
        "G1": (0.5, MAIN_Y), "B1": (1.5, MAIN_Y),
        "BR1": (2.5, MAIN_Y), "R1": (2.5, RELAY_Y),
        "BR2": (4.5, MAIN_Y), "R2": (4.5, RELAY_Y),
        "B2": (5.5, MAIN_Y),
        "BR3": (6.5, MAIN_Y), "R3": (6.5, RELAY_Y),
        "BR4": (8.5, MAIN_Y), "R4": (8.5, RELAY_Y),
        "B3": (9.5, MAIN_Y), "G2": (10.5, MAIN_Y)
    }

    # =========================
    # GENERATORS
    # =========================
    for g in ["G1", "G2"]:
        x, y = pos[g]
        c = color_map.get(generator[g], "#9ca3af")

        if selected == g:
            fig.add_shape(
                type="circle",
                x0=x-0.45, y0=y-0.45,
                x1=x+0.45, y1=y+0.45,
                fillcolor=HIGHLIGHT_COLOR,
                opacity=HIGHLIGHT_OPACITY,
                line=dict(width=0)
            )

        fig.add_shape(
            type="circle",
            x0=x-0.3, y0=y-0.3,
            x1=x+0.3, y1=y+0.3,
            line_color="#60a5fa",
            line_width=3,
            fillcolor=c
        )

        fig.add_annotation(x=x, y=y, text="~", showarrow=False)
        fig.add_annotation(x=x, y=y-0.6, text=g, showarrow=False, font=dict(color=font_color))

    # =========================
    # LINES
    # =========================
    line_positions = {
        "L1": (0.75, 5.5, 3.5),
        "L2": (5.5, 10.25, 7.5)
    }

    for line_key, (x0, x1, label_x) in line_positions.items():

        state = line_status[line_key]
        model_state = line_model.get(line_key)

        if selected == line_key:
            fig.add_shape(
                type="line",
                x0=x0, y0=MAIN_Y,
                x1=x1, y1=MAIN_Y,
                line=dict(color=LINE_HIGHLIGHT_COLOR, width=12)
            )
        else:
            fig.add_shape(
                type="line",
                x0=x0, y0=MAIN_Y,
                x1=x1, y1=MAIN_Y,
                line=dict(color=color_map[state], width=8 if state == "🔴" else 5)
            )

        fig.add_annotation(
            x=label_x, y=MAIN_Y+0.4,
            text=line_key,
            showarrow=False,
            font=dict(color=font_color, size=20)
        )

        if model_state and model_state != state and selected != line_key:
            fig.add_annotation(
                x=label_x,
                y=MAIN_Y+0.9,
                text="⚠️",
                showarrow=False,
                font=dict(size=20, color="#ef4444")
            )

    # =========================
    # BUS
    # =========================
    for b in ["B1", "B2", "B3"]:
        x, y = pos[b]

        if selected == b:
            fig.add_shape(
                type="line",
                x0=x, y0=BUS_BOTTOM,
                x1=x, y1=BUS_TOP,
                line=dict(width=10, color=HIGHLIGHT_COLOR),
                opacity=0.5
            )

        fig.add_shape(
            type="line",
            x0=x, y0=BUS_BOTTOM,
            x1=x, y1=BUS_TOP,
            line=dict(width=6, color=bus_color)
        )

        fig.add_annotation(x=x+0.3, y=BUS_BOTTOM, text=b, showarrow=False)

    # =========================
    # BREAKERS
    # =========================
    for br in ["BR1","BR2","BR3","BR4"]:
        x, y = pos[br]
        c = color_map.get(breaker[br], "#9ca3af")

        if selected == br:
            fig.add_shape(
                type="rect",
                x0=x-0.6, y0=y-0.35,
                x1=x+0.6, y1=y+0.35,
                fillcolor=HIGHLIGHT_COLOR,
                opacity=HIGHLIGHT_OPACITY,
                line=dict(width=0)
            )

        fig.add_shape(
            type="rect",
            x0=x-0.35, y0=y-0.2,
            x1=x+0.35, y1=y+0.2,
            fillcolor=c,
            line_color=line_base_color
        )

        fig.add_annotation(x=x, y=y+0.5, text=br, showarrow=False)

    # =========================
    # BUS → RELAY
    # =========================
    for b_name, r_name in [("B1","R1"),("B2","R2"),("B2","R3"),("B3","R4")]:
        bx, _ = pos[b_name]
        rx, ry = pos[r_name]

        fig.add_shape(
            type="line",
            x0=bx, y0=ry,
            x1=rx, y1=ry,
            line=dict(color="#cbd5f5", width=4, dash="dot"),
            layer="below"
        )

    # =========================
    # BREAKER → RELAY
    # =========================
    for br, r in [("BR1","R1"),("BR2","R2"),("BR3","R3"),("BR4","R4")]:
        bx, _ = pos[br]
        rx, ry = pos[r]

        fig.add_shape(
            type="line",
            x0=bx,
            y0=MAIN_Y - 0.2,
            x1=rx,
            y1=ry - 0.25,
            line=dict(color="#93c5fd", width=4, dash="dot"),
            layer="below"
        )

    # =========================
    # RELAYS (🔥 FIXED PRIORITY)
    # =========================
    for r in ["R1","R2","R3","R4"]:
        x, y = pos[r]

        if r in control.get("isolated", set()):
            c = color_map["⚪"]
        elif r in control.get("locked", set()):
            c = color_map["🟣"]
        else:
            c = color_map.get(relay[r]["color"], "#9ca3af")

        if selected == r:
            fig.add_shape(
                type="rect",
                x0=x-0.8, y0=y-0.45,
                x1=x+0.8, y1=y+0.45,
                fillcolor=HIGHLIGHT_COLOR,
                opacity=HIGHLIGHT_OPACITY,
                line=dict(width=0)
            )

        fig.add_shape(
            type="rect",
            x0=x-0.6, y0=y-0.25,
            x1=x+0.6, y1=y+0.25,
            fillcolor=c,
            line_color=line_base_color
        )

        fig.add_annotation(
            x=x, y=y,
            text=r,
            showarrow=False,
            font=dict(color="white", size=16)
        )

    # =========================
    # 🔥 BADGE SYSTEM (FINAL FIX)
    # =========================
    badges = []
    severity = "none"

    override_lines = set()

    for r in control.get("isolated", set()).union(control.get("locked", set())):
        line = RELAY_TO_LINE.get(r)
        if line:
            override_lines.add(line)

    if override_lines:
        for l in override_lines:
            badges.append(f"🛠 Operator override on {l}")
        severity = "warning"

    else:
        for l in ["L1", "L2"]:
            model_state = line_model.get(l)
            actual_state = line_status[l]

            if model_state and model_state != actual_state:
                badges.append(f"⚠️ Model inconsistency on {l}")

        if len(badges) == 1:
            severity = "warning"
        elif len(badges) >= 2:
            severity = "critical"

    if severity == "critical":
        bg = "#ef4444"
    elif severity == "warning":
        bg = "#f89e01"
    else:
        bg = None

    if badges:
        text = " | ".join(badges)
        fig.add_annotation(
            x=0.97,
            y=0.97,
            xref="paper",
            yref="paper",
            text=f"<b>{text}</b>",
            showarrow=False,
            font=dict(size=16, color="white"),
            align="left",
            bgcolor=bg,
            bordercolor=bg,
            borderwidth=2,
            borderpad=8
        )

    # =========================
    # CLICKABLE LAYER (UNCHANGED)
    # =========================
    names, xs, ys = [], [], []

    for name, (x, y) in pos.items():
        names.append(name)
        xs.append(x)
        ys.append(y)

    line_click_pos = {
        "L1": ((0.75 + 5.5) / 2, MAIN_Y),
        "L2": ((5.5 + 10.25) / 2, MAIN_Y)
    }

    for name, (x, y) in line_click_pos.items():
        names.append(name)
        xs.append(x)
        ys.append(y)

    fig.add_trace(go.Scatter(
        x=xs,
        y=ys,
        mode="markers",
        marker=dict(size=35, color="rgba(0,0,0,0)"),
        text=names,
        hoverinfo="text",
        showlegend=False
    ))

    fig.update_layout(
        template="plotly_dark" if theme == "dark" else "plotly_white",
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False, range=[0,11], scaleanchor="y"),
        yaxis=dict(visible=False, range=[4.5,7.5], scaleanchor="x"),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig