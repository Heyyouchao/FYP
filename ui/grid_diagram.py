import plotly.graph_objects as go

def draw_grid(physical_layer):

    relay = physical_layer["relay"]

    color_map = {
        "🔴": "#ef4444",
        "🟡": "#f59e0b",
        "🟢": "#10b981"
    }

    fig = go.Figure()

    # =========================
    # POSITIONS
    # =========================
    pos = {

        # TOP (POWER)
        "G1": (0, 6),
        "BR1": (1.5, 6),
        "B1": (2.5, 6),

        "BR2": (4, 6),
        "B2": (5, 6),

        "BR3": (6, 6),
        "B3": (7, 6),

        "BR4": (8.5, 6),
        "G2": (10, 6),

        # RELAYS
        "R1": (1.5, 4.8),
        "R2": (4, 4.8),
        "R3": (6, 4.8),
        "R4": (8.5, 4.8),

        # SUBSTATION
        "SW": (5, 3.5),

        # CONTROL ROOM
        "PDC": (7.5, 2),
        "SNORT": (2, 2),
        "SYSLOG": (3.5, 2),
        "CTRL": (5, 1),
        "OPENPDC": (8.5, 1)
    }

    # =========================
    # GENERATORS
    # =========================
    for g in ["G1", "G2"]:
        x, y = pos[g]
        fig.add_shape(
            type="circle",
            x0=x-0.3, y0=y-0.3,
            x1=x+0.3, y1=y+0.3,
            line_color="#60a5fa", line_width=3
        )
        fig.add_annotation(x=x, y=y-0.6, text=g, showarrow=False)

    # =========================
    # MAIN LINE
    # =========================
    fig.add_shape(type="line", x0=0.3, y0=6, x1=9.7, y1=6,
                  line=dict(color="#e5e7eb", width=4))

    # =========================
    # BUSES
    # =========================
    for b in ["B1","B2","B3"]:
        x,y = pos[b]
        fig.add_shape(type="line",
                      x0=x, y0=5.5, x1=x, y1=6.5,
                      line=dict(width=6,color="white"))
        fig.add_annotation(x=x, y=6.8, text=b, showarrow=False)

    # =========================
    # BREAKERS
    # =========================
    for br in ["BR1","BR2","BR3","BR4"]:
        x,y = pos[br]
        fig.add_shape(type="rect",
                      x0=x-0.4, y0=y-0.2,
                      x1=x+0.4, y1=y+0.2,
                      fillcolor="#111827",
                      line_color="white")
        fig.add_annotation(x=x, y=y+0.5, text=br, showarrow=False)

    # =========================
    # CONNECTION LINES
    # =========================
    connections = [
        ("G1","BR1"),("BR1","B1"),
        ("B1","BR2"),("BR2","B2"),
        ("B2","BR3"),("BR3","B3"),
        ("B3","BR4"),("BR4","G2")
    ]

    for a,b in connections:
        x0,y0 = pos[a]
        x1,y1 = pos[b]
        fig.add_shape(type="line",
                      x0=x0,y0=y0,x1=x1,y1=y1,
                      line=dict(color="#9ca3af",width=3))

    # =========================
    # RELAYS (COLORED)
    # =========================
    for r in ["R1","R2","R3","R4"]:
        x,y = pos[r]
        c = color_map[relay[r]]

        # vertical link
        fig.add_shape(type="line",
                      x0=x,y0=6,
                      x1=x,y1=y+0.2,
                      line=dict(color="#6b7280"))

        # box
        fig.add_shape(type="rect",
                      x0=x-0.6,y0=y-0.25,
                      x1=x+0.6,y1=y+0.25,
                      fillcolor=c,line_color=c)

        fig.add_annotation(x=x,y=y-0.6,text=r,showarrow=False)

    # =========================
    # SUBSTATION SWITCH
    # =========================
    x,y = pos["SW"]
    fig.add_shape(type="rect",
                  x0=x-1,y0=y-0.3,
                  x1=x+1,y1=y+0.3,
                  fillcolor="#1f2937",
                  line_color="white")

    fig.add_annotation(x=x,y=y+0.6,text="Substation Switch",showarrow=False)

    # =========================
    # RELAY → SWITCH ARROWS
    # =========================
    for r in ["R1","R2","R3","R4"]:
        x0,y0 = pos[r]
        x1,y1 = pos["SW"]

        fig.add_annotation(
            x=x1,y=y1,
            ax=x0, ay=y0,
            showarrow=True,
            arrowcolor="#9ca3af"
        )

    # =========================
    # CONTROL ROOM
    # =========================
    def box(name,label):
        x,y = pos[name]
        fig.add_shape(type="rect",
                      x0=x-0.6,y0=y-0.3,
                      x1=x+0.6,y1=y+0.3,
                      fillcolor="#111827",
                      line_color="white")
        fig.add_annotation(x=x,y=y,text=label,showarrow=False)

    box("SNORT","Snort")
    box("SYSLOG","Syslog")
    box("CTRL","Control Panel")
    box("OPENPDC","OpenPDC")
    box("PDC","PDC")

    # =========================
    # SWITCH → CONTROL LINKS
    # =========================
    for node in ["PDC","CTRL","SYSLOG","SNORT","OPENPDC"]:
        x0,y0 = pos["SW"]
        x1,y1 = pos[node]

        fig.add_annotation(
            x=x1,y=y1,
            ax=x0, ay=y0,
            showarrow=True,
            arrowcolor="#3b82f6"
        )

    # =========================
    # LAYOUT
    # =========================
    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=10,r=10,t=10,b=10),
        xaxis=dict(visible=False, range=[-1,11]),
        yaxis=dict(visible=False, range=[0,7]),
        showlegend=False
    )

    return fig