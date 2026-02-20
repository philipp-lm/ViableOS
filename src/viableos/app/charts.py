"""Plotly charts for the ViableOS dashboard."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

VIABLEOS_COLORS = {
    "primary": "#6366f1",
    "secondary": "#8b5cf6",
    "accent": "#06b6d4",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "muted": "#64748b",
    "bg": "#0f172a",
    "card": "#1e293b",
    "text": "#f8fafc",
}


def budget_donut(allocations: list[dict[str, Any]], total: float) -> go.Figure:
    """Donut chart showing budget allocation by system."""
    labels = [a["system"] for a in allocations]
    values = [a["monthly_usd"] for a in allocations]

    colors_cycle = [
        VIABLEOS_COLORS["primary"],
        VIABLEOS_COLORS["secondary"],
        VIABLEOS_COLORS["accent"],
        VIABLEOS_COLORS["success"],
        VIABLEOS_COLORS["warning"],
        "#ec4899",
        "#8b5cf6",
        "#14b8a6",
    ]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors_cycle[: len(labels)]),
                textinfo="label+percent",
                textfont=dict(color="white", size=12),
                hovertemplate="<b>%{label}</b><br>$%{value:.0f}/mo<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        annotations=[
            dict(
                text=f"${total:.0f}<br><span style='font-size:12px'>/ month</span>",
                x=0.5,
                y=0.5,
                font=dict(size=24, color="white"),
                showarrow=False,
            )
        ],
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20),
        height=300,
    )
    return fig


def model_tier_bar(routing: dict[str, str]) -> go.Figure:
    """Horizontal bar chart showing which model each system uses."""
    tier_order = {"haiku": 1, "mini": 1.5, "sonnet": 2, "gpt-4o": 2.5, "opus": 3, "o3": 3}
    tier_colors = {1: VIABLEOS_COLORS["success"], 1.5: VIABLEOS_COLORS["success"],
                   2: VIABLEOS_COLORS["warning"], 2.5: VIABLEOS_COLORS["warning"],
                   3: VIABLEOS_COLORS["danger"]}

    labels = []
    scores = []
    colors = []
    model_names = []

    friendly = {
        "s1_routine": "S1 Routine",
        "s1_complex": "S1 Complex",
        "s2_coordination": "S2 Coordinator",
        "s3_optimization": "S3 Optimizer",
        "s3_star_audit": "S3* Auditor",
        "s4_intelligence": "S4 Scout",
        "s5_preparation": "S5 Guardian",
    }

    for key in ["s1_routine", "s1_complex", "s2_coordination", "s3_optimization",
                "s3_star_audit", "s4_intelligence", "s5_preparation"]:
        model = routing.get(key, "unknown")
        model_short = model.split("/")[-1] if "/" in model else model
        tier = 2
        for kw, score in tier_order.items():
            if kw in model.lower():
                tier = score
                break

        labels.append(friendly.get(key, key))
        scores.append(tier)
        colors.append(tier_colors.get(tier, VIABLEOS_COLORS["muted"]))
        model_names.append(model_short)

    fig = go.Figure(
        data=[
            go.Bar(
                y=labels,
                x=scores,
                orientation="h",
                marker=dict(color=colors),
                text=model_names,
                textposition="inside",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            range=[0, 3.5],
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#94a3b8", size=11),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=120, r=20),
        height=260,
    )
    return fig


def vsm_overview_diagram(config: dict[str, Any]) -> go.Figure:
    """Visual VSM system diagram showing connections between systems."""
    vs = config.get("viable_system", {})
    s1_units = vs.get("system_1", [])
    has_s2 = bool(vs.get("system_2", {}).get("coordination_rules"))
    has_s3 = bool(vs.get("system_3"))
    has_s3star = bool(vs.get("system_3_star"))
    has_s4 = bool(vs.get("system_4"))

    fig = go.Figure()

    # S5 at top
    fig.add_trace(go.Scatter(
        x=[0.5], y=[1.0],
        mode="markers+text",
        marker=dict(size=50, color=VIABLEOS_COLORS["primary"], symbol="diamond"),
        text=["S5<br>Policy"],
        textposition="middle center",
        textfont=dict(color="white", size=10),
        hoverinfo="text",
        hovertext="S5 — Policy Guardian: enforces values, prepares decisions for humans",
    ))

    # S4 (left) and S3 (right) flanking center
    fig.add_trace(go.Scatter(
        x=[0.15], y=[0.65],
        mode="markers+text",
        marker=dict(size=45, color=VIABLEOS_COLORS["accent"] if has_s4 else VIABLEOS_COLORS["muted"], symbol="diamond"),
        text=["S4<br>Scout"],
        textposition="middle center",
        textfont=dict(color="white", size=10),
        hoverinfo="text",
        hovertext="S4 — Intelligence: monitors environment, strategic briefs",
    ))

    fig.add_trace(go.Scatter(
        x=[0.85], y=[0.65],
        mode="markers+text",
        marker=dict(size=45, color=VIABLEOS_COLORS["warning"] if has_s3 else VIABLEOS_COLORS["muted"], symbol="diamond"),
        text=["S3<br>Optimizer"],
        textposition="middle center",
        textfont=dict(color="white", size=10),
        hoverinfo="text",
        hovertext="S3 — Optimization: manages resources, weekly digest",
    ))

    # S3* (near S3)
    fig.add_trace(go.Scatter(
        x=[0.75], y=[0.45],
        mode="markers+text",
        marker=dict(size=35, color=VIABLEOS_COLORS["danger"] if has_s3star else VIABLEOS_COLORS["muted"], symbol="star"),
        text=["S3*"],
        textposition="middle center",
        textfont=dict(color="white", size=10),
        hoverinfo="text",
        hovertext="S3* — Auditor: independent quality checks",
    ))

    # S2 coordinator line
    fig.add_trace(go.Scatter(
        x=[0.5], y=[0.35],
        mode="markers+text",
        marker=dict(size=40, color=VIABLEOS_COLORS["success"] if has_s2 else VIABLEOS_COLORS["muted"], symbol="diamond"),
        text=["S2<br>Coord"],
        textposition="middle center",
        textfont=dict(color="white", size=9),
        hoverinfo="text",
        hovertext="S2 — Coordinator: prevents conflicts between operational units",
    ))

    # S1 units at bottom
    n = len(s1_units)
    for i, unit in enumerate(s1_units):
        x_pos = (i + 0.5) / max(n, 1)
        fig.add_trace(go.Scatter(
            x=[x_pos], y=[0.1],
            mode="markers+text",
            marker=dict(size=40, color=VIABLEOS_COLORS["secondary"]),
            text=[f"S1<br>{unit.get('name', '?')[:10]}"],
            textposition="middle center",
            textfont=dict(color="white", size=8),
            hoverinfo="text",
            hovertext=f"S1 — {unit.get('name', '?')}: {unit.get('purpose', '')}",
        ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, range=[-0.1, 1.1]),
        yaxis=dict(showgrid=False, showticklabels=False, range=[-0.05, 1.15]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=10, b=10, l=10, r=10),
        height=400,
    )
    return fig
