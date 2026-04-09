import streamlit as st
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.set_page_config(layout="wide")

from engine.explainer import(
    get_relay_flow,
    get_breaker_flow, 
    get_line_flow, 
    get_bus_flow, 
    get_generator_flow, 
    get_cyber_logs
)

# ============================================================
# SESSION STATE
# ============================================================
if "control_state" not in st.session_state:
    st.session_state.control_state = {
        "isolated": set(),
        "locked": set()
    }

if "selected_component" not in st.session_state:
    st.session_state.selected_component = None

# ============================================================
# RELAY → LINE MAP
# ============================================================
RELAY_TO_LINE = {
    "R1": "L1",
    "R2": "L1",
    "R3": "L2",
    "R4": "L2",
}

# ============================================================
# BASE PHYSICAL LAYER
# ============================================================
def get_base_physical_layer():
    return {
        "relay": {
            "R1": {"color": "🟢"},
            "R2": {"color": "🟢"},
            "R3": {"color": "🟢"},
            "R4": {"color": "🟢"},
        },
        "generator": {
            "G1": "🟢",
            "G2": "🟢",
        },
        "bus": {
            "B1": "🟢",
            "B2": "🟢",
            "B3": "🟢",
        },
        "breaker": {
            "BR1": "🟢",
            "BR2": "🟢",
            "BR3": "🟢",
            "BR4": "🟢",
        },
        "line": {
            "L1": "🟢",
            "L2": "🟢",
        },
        "line_model": {
            "L1": "🟢",
            "L2": "🟢",
        }
    }

# ============================================================
# APPLY USER CONTROLS
# ============================================================
def apply_user_controls(physical_layer):
    control = st.session_state.control_state

    relay = physical_layer["relay"]
    breaker = physical_layer["breaker"]
    line = physical_layer["line"]
    bus = physical_layer["bus"]

    # reset base state
    for r in relay:
        relay[r]["color"] = "🟢"

    for br in breaker:
        breaker[br] = "🟢"

    for l in line:
        line[l] = "🟢"

    for b in bus:
        bus[b] = "🟢"

    # isolate logic
    for r in control["isolated"]:
        relay[r]["color"] = "⚪"

        affected_line = RELAY_TO_LINE.get(r)

        if affected_line == "L1":
            line["L1"] = "⚪"
            breaker["BR1"] = "🔴"
            breaker["BR2"] = "🔴"
            bus["B1"] = "🟡"
            bus["B2"] = "🟡"

        elif affected_line == "L2":
            line["L2"] = "⚪"
            breaker["BR3"] = "🔴"
            breaker["BR4"] = "🔴"
            bus["B2"] = "🟡"
            bus["B3"] = "🟡"

    # lock logic
    for r in control["locked"]:
        relay[r]["color"] = "🟣"

        affected_line = RELAY_TO_LINE.get(r)

        if affected_line == "L1":
            line["L1"] = "🔴"

        elif affected_line == "L2":
            line["L2"] = "🔴"

    return physical_layer

# ============================================================
# DRAW GRID
# ============================================================
def draw_grid(physical_layer, selected=None):
    relay = physical_layer["relay"]
    generator = physical_layer["generator"]
    bus = physical_layer["bus"]
    breaker = physical_layer["breaker"]
    line_status = physical_layer["line"]
    line_model = physical_layer.get("line_model", {})

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

    # generators
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

    # lines
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

    # bus
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

    # breakers
    for br in ["BR1", "BR2", "BR3", "BR4"]:
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

    # bus -> relay
    for b_name, r_name in [("B1", "R1"), ("B2", "R2"), ("B2", "R3"), ("B3", "R4")]:
        bx, _ = pos[b_name]
        rx, ry = pos[r_name]

        fig.add_shape(
            type="line",
            x0=bx, y0=ry,
            x1=rx, y1=ry,
            line=dict(color="#cbd5f5", width=4, dash="dot"),
            layer="below"
        )

    # breaker -> relay
    for br, r in [("BR1", "R1"), ("BR2", "R2"), ("BR3", "R3"), ("BR4", "R4")]:
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

    # relays
    for r in ["R1", "R2", "R3", "R4"]:
        x, y = pos[r]
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

        text_color = "white" if relay[r]["color"] != "⚪" else "#111827"
        fig.add_annotation(
            x=x, y=y,
            text=r,
            showarrow=False,
            font=dict(color=text_color, size=16)
        )

    # badge system
    badges = []
    severity = "none"

    control = st.session_state.get("control_state", {})
    isolated = control.get("isolated", set())
    locked = control.get("locked", set())

    override_lines = set()

    for r in list(isolated) + list(locked):
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
                if model_state == "🟢" and actual_state == "🔴":
                    badges.append(f"⚠️ Injection detected in {l}")
                elif model_state == "🔴" and actual_state == "🟢":
                    badges.append(f"⚠️ Relay failure on {l}")
                else:
                    badges.append(f"⚠️ Model inconsistency on {l}")

        if len(badges) == 1:
            severity = "warning"
        elif len(badges) >= 2:
            severity = "critical"

    if severity == "critical":
        bg = "#ef4444"
    elif severity == "warning":
        bg = "#f59e0b"
    else:
        bg = None

    if badges:
        text = " | ".join(badges)
        fig.add_annotation(
            x=0.97,
            y=0.97,
            xref="paper",
            yref="paper",
            text=text,
            showarrow=False,
            font=dict(size=14, color="white"),
            align="left",
            bgcolor=bg,
            bordercolor=bg,
            borderwidth=2,
            borderpad=6
        )

    # clickable layer
    names = []
    xs = []
    ys = []

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
        xaxis=dict(visible=False, range=[0, 11], scaleanchor="y"),
        yaxis=dict(visible=False, range=[4.5, 7.5], scaleanchor="x"),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig

# ============================================================
# UI
# ============================================================
st.title("Grid Controls Debug")

col_top_left, col_top_right = st.columns([2, 1])

with col_top_left:
    selected = st.selectbox("Target relay", ["R1", "R2", "R3", "R4"])
    if st.button("Restore All", use_container_width=True):
        st.session_state.control_state["isolated"].clear()
        st.session_state.control_state["locked"].clear()
        st.rerun()
with col_top_right:
    st.markdown("### Actions")
    a1, a2, a3 = st.columns(3)

    with a1:
        if st.button("🔌 Isolate", use_container_width=True):
            st.session_state.control_state["isolated"].add(selected)
            st.session_state.control_state["locked"].discard(selected)
            st.rerun()

    with a2:
        if st.button("🔒 Lock", use_container_width=True):
            st.session_state.control_state["locked"].add(selected)
            st.session_state.control_state["isolated"].discard(selected)
            st.rerun()

    with a3:
        if st.button("🛠 Restore", use_container_width=True):
            st.session_state.control_state["isolated"].discard(selected)
            st.session_state.control_state["locked"].discard(selected)
            st.rerun()

physical_layer = get_base_physical_layer()
physical_layer = apply_user_controls(physical_layer)

col_left, col_right = st.columns([2, 1])
with col_left:  
    fig_grid = draw_grid(
        physical_layer,
        selected=st.session_state.get("selected_component")
    )

    selected_points = plotly_events(
        fig_grid, 
        click_event=True,
        hover_event=False,
        select_event=False,
        override_height=420,
    )

    if selected_points:

        point = selected_points[0]
        idx = point["pointIndex"]

        clickable_trace = fig_grid.data[-1]
        selected_name = clickable_trace["text"][idx]


        if st.session_state.selected_component == selected_name:
            st.session_state.selected_component = None
        else:
            st.session_state.selected_component = selected_name

        st.rerun()
with col_right:
    # ============================================================
    # 🔍 SELECTED COMPONENT PANEL (DASHBOARD STYLE)
    # ============================================================
    st.markdown("### 🖥️ Control Panel")

    selected = st.session_state.get("selected_component")

    if not selected:
        st.markdown("""
        <div style="
            margin: 30px auto;
            padding: 16px 20px;
            width: 65%;
            border-radius: 14px;
            background: linear-gradient(145deg, rgba(30,41,59,0.6), rgba(15,23,42,0.6));
            border: 1px solid rgba(148,163,184,0.2);
            text-align: center;
            color: #cbd5f5;
            font-size: 14px;
            font-weight: 500;
            backdrop-filter: blur(6px);
        ">
            Click a component in the grid
        </div>
        """, unsafe_allow_html=True)

    else:

        breaker = physical_layer.get("breaker", {})
        line_status = physical_layer.get("line", {})
        line_model = physical_layer.get("line_model", {})
        bus = physical_layer.get("bus", {})
        generator = physical_layer.get("generator", {})

        # =========================
        # RELAY
        # =========================
        if selected.startswith("R"):

            r_data = physical_layer["relay"][selected]

            raw = raw_scores[selected]
            norm = norm_scores[selected]

            # 🔥 HEADER
            control = st.session_state.control_state
            if selected in control["isolated"]:
                relay_color = "⚪️"
                status = "Isolated"
            elif selected in control["locked"]:
                relay_color = "🟣"
                status = "Locked"
            else:
                relay_color = r_data["color"]
                status = "Normal" if relay_color == "🟢" else "Alert"

            st.markdown(f"### Selected - {selected} {relay_color}({status})")

            # 🔥 ROW: score + chain
            flow = get_relay_flow(selected)

            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.markdown(f"Raw: {raw:.2f} | Norm: {norm:.2f}")
            with c2:
                st.markdown(f" Event Chain: {flow['affected_by']} → {flow['affects_on']}")

            # =========================
            # CAUSE (INLINE)
            # =========================
            if "top_features" in r_data:

                causes = []

                for f in r_data["top_features"][:3]:
                    name = readable_feature_pop(f)
                    name = name.split(" ", 1)[1] if " " in name else name
                    causes.append(name)

                st.markdown(f"**Cause:** {' | '.join(causes)}")

            # =========================
            # CYBER (INLINE)
            # =========================
            logs = get_cyber_logs(row_clean, selected)

            st.markdown(f"**Cyber:** {' | '.join(logs)}")

        # =========================
        # NON-RELAY (IMPROVED)
        # =========================
        else:
            
            # =========================
            # SELECTED HEADER (ONLY G + B COLORED)
            # =========================
            if selected.startswith("G") or (selected.startswith("B") and not selected.startswith("BR")):

                # get correct state
                if selected.startswith("B"):
                    state = bus.get(selected, "⚪")
                else:  # G
                    state = generator.get(selected, "⚪")

                # map emoji → color
                color_map = {
                    "🟢": "#22c55e",
                    "🔴": "#ef4444",
                    "🟡": "#f59e0b",
                    "⚪": "#9ca3af"
                }

                dot_color = color_map.get(state, "#9ca3af")

                st.markdown(f"""
                <h3>
                Selected — {selected}
                <span style="
                    display:inline-block;
                    width:10px;
                    height:10px;
                    border-radius:50%;
                    background:{dot_color};
                    margin-left:8px;
                "></span>
                </h3>
                """, unsafe_allow_html=True)

            else:
                # normal (no color)
                st.markdown(f"### Selected — `{selected}`")

            # =========================
            # BREAKER
            # =========================
            if selected.startswith("BR"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Status:** {status}")

                flow = get_breaker_flow(selected)

                with c2:
                    st.markdown(f"**Chain:** {flow['affected_by']} → {flow['affects_on']}")
                st.caption("Protection switch controlling line flow")

            # =========================
            # GENERATOR
            # =========================
            elif selected.startswith("G"):

                flow = get_generator_flow(selected)

                st.markdown(f"**Chain:** {flow['affected_by']} → {flow['affects_on']}")
                st.caption("Power source supplying the grid")

            # =========================
            # BUS
            # =========================
            elif selected.startswith("B"):

                flow = get_bus_flow(selected)

                st.markdown(f"**Chain:** {flow['affected_by']} → {flow['affects_on']}")
                st.caption("Connection node distributing power")

            # =========================
            # LINE
            # =========================

            elif selected.startswith("L"):
                actual = physical_layer["line"].get(selected, "N/A")
                model = physical_layer["line_model"].get(selected, "N/A")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="mini-box">
                        <div class="mini-label">State</div>
                        <div class="mini-value">{actual}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="mini-box">
                        <div class="mini-label">Model</div>
                        <div class="mini-value">{model}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # =========================
                # FLOW / CHAIN
                # =========================
                flow = get_line_flow(selected)

                st.markdown(f"""
                <div class="chain-box">
                    <b>Chain:</b> {flow['affected_by']} → {flow['affects_on']}
                </div>
                """, unsafe_allow_html=True)

                st.caption("Transmission path between buses")


        # =========================
        # CLEAR
        # =========================
        if st.button("Clear", use_container_width=True):
            st.session_state.selected_component = None
            st.rerun()

st.markdown("### Debug state")
st.write(st.session_state.control_state)