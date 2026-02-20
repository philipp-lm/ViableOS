"""Plotly charts and HTML components for the ViableOS dashboard."""

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

# Color scheme matching the VSM diagram HTML reference
_VSM_COLORS = {
    "s5": {"bg": "linear-gradient(135deg, #312e81, #3730a3)", "border": "#6366f1", "badge": "#6366f1", "text": "#c7d2fe"},
    "s4": {"bg": "linear-gradient(135deg, #164e63, #155e75)", "border": "#06b6d4", "badge": "#06b6d4", "text": "#a5f3fc"},
    "s3star": {"bg": "linear-gradient(135deg, #831843, #9d174d)", "border": "#ec4899", "badge": "#ec4899", "text": "#fbcfe8"},
    "s3": {"bg": "linear-gradient(135deg, #78350f, #92400e)", "border": "#f59e0b", "badge": "#f59e0b", "text": "#fde68a"},
    "s2": {"bg": "linear-gradient(135deg, #14532d, #166534)", "border": "#10b981", "badge": "#10b981", "text": "#a7f3d0"},
    "s1": {"bg": "linear-gradient(135deg, #1e293b, #334155)", "border": "#94a3b8", "badge": "#64748b", "text": "#cbd5e1"},
}


def vsm_diagram_html(config: dict[str, Any]) -> str:
    """Generate an HTML VSM diagram matching the reference layout."""
    vs = config.get("viable_system", {})
    identity = vs.get("identity", {})
    s1_units = vs.get("system_1", [])
    s2_rules = vs.get("system_2", {}).get("coordination_rules", [])
    s3_cfg = vs.get("system_3", {})
    s3star_cfg = vs.get("system_3_star", {})
    s4_cfg = vs.get("system_4", {})
    hitl = vs.get("human_in_the_loop", {})

    has_s2 = bool(s2_rules)
    has_s3 = bool(s3_cfg.get("reporting_rhythm") or s3_cfg.get("resource_allocation"))
    has_s3star = bool(s3star_cfg.get("checks"))
    has_s4 = bool(s4_cfg.get("monitoring"))

    # S1 unit items
    unit_html = ""
    for u in s1_units:
        unit_html += f"""<div style="display:flex;align-items:baseline;gap:6px;font-size:11px;
            color:#cbd5e1;padding:2px 0;">
            <span style="color:#94a3b8;font-size:8px;">●</span>
            <strong style="color:#f8fafc;">{u.get('name','?')}</strong> — {u.get('purpose','')[:50]}
        </div>"""

    # S2 rules
    rules_html = ""
    for r in s2_rules[:3]:
        rules_html += f"""<div style="font-size:11px;color:{_VSM_COLORS['s2']['text']};padding:2px 0 2px 12px;position:relative;">
            <span style="position:absolute;left:0;font-weight:700;">›</span>
            {r.get('trigger','')[:40]} → {r.get('action','')[:40]}
        </div>"""
    if not rules_html:
        rules_html = '<div style="font-size:11px;color:#64748b;font-style:italic;">Not configured yet</div>'

    # S3 info
    s3_rhythm = s3_cfg.get("reporting_rhythm", "—")
    s3_alloc = s3_cfg.get("resource_allocation", "—")

    # S3* checks
    checks_html = ""
    for c in s3star_cfg.get("checks", [])[:3]:
        checks_html += f"""<div style="font-size:11px;color:{_VSM_COLORS['s3star']['text']};padding:2px 0 2px 12px;position:relative;">
            <span style="position:absolute;left:0;font-weight:700;">›</span>
            <strong>{c.get('name','')}</strong> → {c.get('target','')}
        </div>"""
    if not checks_html:
        checks_html = '<div style="font-size:11px;color:#64748b;font-style:italic;">Not configured yet</div>'

    # S4 monitoring
    monitoring = s4_cfg.get("monitoring", {})
    s4_items = monitoring.get("competitors", [])[:2] + monitoring.get("technology", [])[:2]
    s4_html = ""
    for item in s4_items:
        s4_html += f"""<div style="font-size:11px;color:{_VSM_COLORS['s4']['text']};padding:2px 0 2px 12px;position:relative;">
            <span style="position:absolute;left:0;font-weight:700;">›</span>{item}
        </div>"""
    if not s4_html:
        s4_html = '<div style="font-size:11px;color:#64748b;font-style:italic;">Not configured yet</div>'

    # S5 info
    purpose = identity.get("purpose", "—")
    values = identity.get("values", [])
    values_html = ", ".join(values[:3]) if values else "—"

    # HiTL summary for S5 box
    approval_count = len(hitl.get("approval_required", []))
    emergency_count = len(hitl.get("emergency_alerts", []))

    def _opacity(present: bool) -> str:
        return "1.0" if present else "0.5"

    return f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: auto auto auto auto;
        gap: 10px;
        max-width: 100%;">

        <!-- S5: Identity — top left -->
        <div style="background: {_VSM_COLORS['s5']['bg']};
            border: 2px solid {_VSM_COLORS['s5']['border']};
            border-radius: 10px; padding: 14px; grid-column: 1; grid-row: 1;">
            <span style="display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;
                border-radius:4px;background:{_VSM_COLORS['s5']['badge']};color:#fff;
                margin-bottom:6px;letter-spacing:0.5px;">S5</span>
            <div style="font-size:14px;font-weight:700;color:#e0e7ff;margin-bottom:6px;">
                Identity & Policy
            </div>
            <div style="font-size:11px;color:{_VSM_COLORS['s5']['text']};margin-bottom:4px;">
                {purpose[:80]}
            </div>
            <div style="font-size:10px;color:#a5b4fc;margin-top:6px;">
                Values: {values_html}
            </div>
            <div style="font-size:10px;color:#a5b4fc;">
                {approval_count} approval gates | {emergency_count} emergency alerts
            </div>
        </div>

        <!-- S4: Intelligence — top right -->
        <div style="background: {_VSM_COLORS['s4']['bg']};
            border: 2px solid {_VSM_COLORS['s4']['border']};
            border-radius: 10px; padding: 14px; grid-column: 2; grid-row: 1;
            opacity: {_opacity(has_s4)};">
            <span style="display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;
                border-radius:4px;background:{_VSM_COLORS['s4']['badge']};color:#fff;
                margin-bottom:6px;letter-spacing:0.5px;">S4</span>
            <div style="font-size:14px;font-weight:700;color:#cffafe;margin-bottom:6px;">
                Intelligence (Scout)
            </div>
            {s4_html}
        </div>

        <!-- S3*: Audit — middle left -->
        <div style="background: {_VSM_COLORS['s3star']['bg']};
            border: 2px solid {_VSM_COLORS['s3star']['border']};
            border-radius: 10px; padding: 14px; grid-column: 1; grid-row: 2;
            opacity: {_opacity(has_s3star)};">
            <span style="display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;
                border-radius:4px;background:{_VSM_COLORS['s3star']['badge']};color:#fff;
                margin-bottom:6px;letter-spacing:0.5px;">S3*</span>
            <div style="font-size:14px;font-weight:700;color:#fce7f3;margin-bottom:6px;">
                Audit
            </div>
            <div style="font-size:10px;color:#f9a8d4;margin-bottom:4px;">
                Independent verification — different AI provider
            </div>
            {checks_html}
        </div>

        <!-- S3: Optimization — middle right -->
        <div style="background: {_VSM_COLORS['s3']['bg']};
            border: 2px solid {_VSM_COLORS['s3']['border']};
            border-radius: 10px; padding: 14px; grid-column: 2; grid-row: 2;
            opacity: {_opacity(has_s3)};">
            <span style="display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;
                border-radius:4px;background:{_VSM_COLORS['s3']['badge']};color:#fff;
                margin-bottom:6px;letter-spacing:0.5px;">S3</span>
            <div style="font-size:14px;font-weight:700;color:#fef3c7;margin-bottom:6px;">
                Optimization (Manager)
            </div>
            <div style="font-size:11px;color:{_VSM_COLORS['s3']['text']};">
                Reporting: {s3_rhythm}
            </div>
            <div style="font-size:11px;color:{_VSM_COLORS['s3']['text']};">
                Resources: {s3_alloc[:60]}
            </div>
        </div>

        <!-- S1: Operations — bottom left (spans full width) -->
        <div style="background: {_VSM_COLORS['s1']['bg']};
            border: 2px solid {_VSM_COLORS['s1']['border']};
            border-radius: 10px; padding: 14px; grid-column: 1 / 3; grid-row: 3;">
            <span style="display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;
                border-radius:4px;background:{_VSM_COLORS['s1']['badge']};color:#fff;
                margin-bottom:6px;letter-spacing:0.5px;">S1</span>
            <div style="font-size:14px;font-weight:700;color:#f8fafc;margin-bottom:8px;">
                Operations — {len(s1_units)} unit{'s' if len(s1_units) != 1 else ''}
            </div>
            {unit_html}
        </div>

        <!-- S2: Coordination — bottom -->
        <div style="background: {_VSM_COLORS['s2']['bg']};
            border: 2px solid {_VSM_COLORS['s2']['border']};
            border-radius: 10px; padding: 14px; grid-column: 1 / 3; grid-row: 4;
            opacity: {_opacity(has_s2)};">
            <span style="display:inline-block;font-size:10px;font-weight:700;padding:2px 8px;
                border-radius:4px;background:{_VSM_COLORS['s2']['badge']};color:#fff;
                margin-bottom:6px;letter-spacing:0.5px;">S2</span>
            <div style="font-size:14px;font-weight:700;color:#d1fae5;margin-bottom:6px;">
                Coordination
            </div>
            {rules_html}
        </div>
    </div>
    """


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
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{label}</b><br>$%{value:.0f}/mo<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        annotations=[
            dict(
                text=f"${total:.0f}<br><span style='font-size:11px'>/ month</span>",
                x=0.5,
                y=0.5,
                font=dict(size=22, color="white"),
                showarrow=False,
            )
        ],
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
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
        margin=dict(t=10, b=10, l=100, r=20),
        height=240,
    )
    return fig
