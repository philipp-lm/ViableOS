"""Dashboard view — VSM overview, budget, agents, HiTL summary, warnings, rollout."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import yaml

from viableos.app.charts import budget_donut, model_tier_bar, vsm_diagram_html
from viableos.app.state import get_config, get_vs
from viableos.budget import FRIENDLY_NAMES, calculate_budget
from viableos.checker import check_viability
from viableos.generator import generate_openclaw_package
from viableos.schema import validate


def render_dashboard() -> None:
    """Main dashboard renderer."""
    config = get_config()
    vs = get_vs()

    if not vs:
        st.warning("No configuration loaded. Run the wizard first.")
        if st.button("Start Wizard"):
            st.session_state["view"] = "wizard"
            st.session_state["wizard_step"] = 0
            st.rerun()
        return

    system_name = vs.get("name", "Unknown System")

    # Top bar
    col_title, col_actions = st.columns([3, 1])
    with col_title:
        st.markdown(f"## {system_name}")
    with col_actions:
        if st.button("Edit in Wizard"):
            st.session_state["view"] = "wizard"
            st.session_state["wizard_step"] = 0
            st.rerun()

    # Validation
    errors = validate(config)
    if errors:
        st.error(f"Configuration has {len(errors)} validation errors")
        for err in errors:
            st.markdown(f"- {err}")
        return

    plan = calculate_budget(config)
    report = check_viability(config)

    # Top metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Viability Score", f"{report.score}/{report.total}")
    with m2:
        st.metric("Monthly Budget", f"${plan.total_monthly_usd:.0f}")
    with m3:
        st.metric("Strategy", plan.strategy.title())
    with m4:
        st.metric("Agents", str(len(plan.allocations)))
    with m5:
        critical_count = sum(1 for w in report.warnings if w.severity == "critical")
        warning_count = sum(1 for w in report.warnings if w.severity == "warning")
        st.metric("Warnings", f"{critical_count}C / {warning_count}W")

    st.divider()

    # ── Warnings panel ────────────────────────────────────────────────────
    if report.warnings:
        critical = [w for w in report.warnings if w.severity == "critical"]
        other = [w for w in report.warnings if w.severity != "critical"]

        if critical:
            for w in critical:
                st.markdown(
                    f"""<div style="padding:10px 14px;border-radius:8px;border-left:4px solid #ef4444;
                    background:#1e293b;margin-bottom:6px;">
                    <span style="color:#ef4444;font-weight:700;font-size:10px;">CRITICAL</span>
                    <span style="color:#94a3b8;font-size:10px;margin-left:8px;">{w.category}</span>
                    <div style="color:#f8fafc;font-size:12px;margin-top:2px;">{w.message}</div>
                    <div style="color:#94a3b8;font-size:11px;">{w.suggestion}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        if other:
            with st.expander(f"Warnings and insights ({len(other)})", expanded=False):
                severity_colors = {"warning": "#f59e0b", "info": "#6366f1"}
                for w in other:
                    color = severity_colors.get(w.severity, "#64748b")
                    st.markdown(
                        f"""<div style="padding:8px 12px;border-radius:6px;border-left:3px solid {color};
                        background:#1e293b;margin-bottom:4px;">
                        <span style="color:{color};font-weight:700;font-size:10px;text-transform:uppercase;">
                            {w.severity}
                        </span>
                        <span style="color:#94a3b8;font-size:10px;margin-left:6px;">{w.category}</span>
                        <div style="color:#f8fafc;font-size:12px;margin-top:2px;">{w.message}</div>
                        <div style="color:#94a3b8;font-size:11px;">{w.suggestion}</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )

        st.divider()

    # Two-column layout: VSM diagram | Budget + Models
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("### System Map")
        diagram = vsm_diagram_html(config)
        components.html(diagram, height=700, scrolling=True)

    with right:
        st.markdown("### Budget Allocation")
        alloc_dicts = [
            {"system": a.system, "monthly_usd": a.monthly_usd, "model": a.model, "percentage": a.percentage}
            for a in plan.allocations
        ]
        fig = budget_donut(alloc_dicts, plan.total_monthly_usd)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### Model Routing")
        fig = model_tier_bar(plan.model_routing)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    # Viability checklist
    st.markdown("### Viability Checklist")
    check_cols = st.columns(3)
    for i, check in enumerate(report.checks):
        with check_cols[i % 3]:
            status = "PASS" if check.present else "MISSING"
            color = "#10b981" if check.present else "#ef4444"
            st.markdown(
                f"""<div style="padding:8px 12px;border-radius:8px;border:1px solid #334155;
                background:#1e293b;margin-bottom:8px;">
                <span style="color:{color};font-weight:700;font-size:11px;">{status}</span>
                <span style="color:#f8fafc;font-weight:600;margin-left:6px;">{check.system} {check.name}</span>
                <div style="font-size:11px;color:#94a3b8;margin-top:2px;">{check.details}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # Agent cards
    st.markdown("### Agent Overview")

    s1_units = vs.get("system_1", [])
    agent_data = []
    for unit in s1_units:
        alloc = next(
            (a for a in plan.allocations if a.system == f"S1:{unit.get('name', '?')}"),
            None,
        )
        agent_data.append({
            "name": unit.get("name", "?"),
            "role": "Operations (S1)",
            "purpose": unit.get("purpose", ""),
            "model": alloc.model if alloc else "?",
            "budget": f"${alloc.monthly_usd:.0f}" if alloc else "?",
            "autonomy": unit.get("autonomy", "Not specified"),
            "tools": ", ".join(unit.get("tools", [])[:4]),
        })

    management_agents = [
        ("Coordinator", "S2", "s2_coordination", "Prevents conflicts between units"),
        ("Optimizer", "S3", "s3_optimization", "Allocates resources, weekly digest"),
        ("Auditor", "S3*", "s3_star_audit", "Independent quality verification"),
        ("Scout", "S4", "s4_intelligence", "Monitors environment, strategic briefs"),
        ("Policy Guardian", "S5", "s5_preparation", "Enforces values and policies"),
    ]
    for mgmt_name, sys_key, routing_key, purpose in management_agents:
        alloc = next((a for a in plan.allocations if a.system == sys_key), None)
        agent_data.append({
            "name": mgmt_name,
            "role": f"{FRIENDLY_NAMES.get(sys_key, sys_key)} ({sys_key})",
            "purpose": purpose,
            "model": plan.model_routing.get(routing_key, "?"),
            "budget": f"${alloc.monthly_usd:.0f}" if alloc else "?",
            "autonomy": "System agent",
            "tools": "",
        })

    cards_html = '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;">'
    for agent in agent_data:
        model_short = agent["model"].split("/")[-1] if "/" in agent["model"] else agent["model"]
        tools_line = f'<div style="font-size:10px;color:#475569;margin-top:2px;">Tools: {agent["tools"]}</div>' if agent["tools"] else ""
        cards_html += f'''<div style="padding:12px;border-radius:8px;border:1px solid #334155;background:#1e293b;">
            <div style="font-weight:700;color:#f8fafc;font-size:14px;">{agent["name"]}</div>
            <div style="font-size:10px;color:#64748b;margin-bottom:4px;">{agent["role"]}</div>
            <div style="font-size:12px;color:#cbd5e1;margin-bottom:4px;">{agent["purpose"]}</div>
            <div style="font-size:10px;color:#475569;margin-top:4px;">
                Model: <span style="color:#94a3b8;font-family:monospace;background:#0f172a;padding:1px 5px;border-radius:3px;">{model_short}</span>
                &nbsp;|&nbsp; {agent["budget"]}/mo
            </div>
            {tools_line}
        </div>'''
    cards_html += '</div>'

    row_count = (len(agent_data) + 2) // 3
    cards_height = row_count * 140 + 20
    components.html(cards_html, height=cards_height, scrolling=False)

    st.divider()

    # HiTL summary
    hitl = vs.get("human_in_the_loop", {})
    if hitl:
        st.markdown("### Human-in-the-Loop")
        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown("**Needs Your Approval**")
            for item in hitl.get("approval_required", []):
                st.markdown(f"- {item}")
        with h2:
            st.markdown("**Sent for Review**")
            for item in hitl.get("review_required", []):
                st.markdown(f"- {item}")
        with h3:
            st.markdown("**Emergency Alerts**")
            for item in hitl.get("emergency_alerts", []):
                st.markdown(f"- {item}")

        st.caption(f"Notification channel: **{hitl.get('notification_channel', 'not set')}**")

    # Never-do boundaries
    never_do = vs.get("identity", {}).get("never_do", [])
    if never_do:
        st.divider()
        st.markdown("### Agent Boundaries (NEVER DO)")
        for item in never_do:
            st.markdown(
                f"<div style='padding:4px 10px;font-size:12px;color:#fca5a5;'>"
                f"<span style='color:#ef4444;font-weight:700;'>X</span> {item}</div>",
                unsafe_allow_html=True,
            )

    # Persistence
    persistence = vs.get("persistence", {})
    if persistence.get("strategy") and persistence["strategy"] != "none":
        st.divider()
        st.markdown("### State Persistence")
        st.markdown(f"Strategy: **{persistence['strategy']}**")
        if persistence.get("path"):
            st.markdown(f"Path: `{persistence['path']}`")

    st.divider()

    # Export
    st.markdown("### Export")

    col_yaml, col_generate = st.columns(2)

    with col_yaml:
        yaml_str = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        st.download_button(
            "Download YAML Config",
            data=yaml_str,
            file_name="viableos.yaml",
            mime="text/yaml",
            use_container_width=True,
        )

    with col_generate:
        if st.button("Generate OpenClaw Package", use_container_width=True, type="primary"):
            with st.spinner("Generating..."):
                with tempfile.TemporaryDirectory() as tmp:
                    out_path = generate_openclaw_package(config, Path(tmp) / "viableos-openclaw")
                    agent_count = len(list(out_path.glob("workspaces/*/SOUL.md")))

                    file_types = ["SOUL.md", "SKILL.md", "HEARTBEAT.md"]
                    st.success(
                        f"Generated {agent_count} agents — each with "
                        f"SOUL.md, SKILL.md, HEARTBEAT.md, USER.md, MEMORY.md, AGENTS.md"
                    )

                    for ws_dir in sorted((out_path / "workspaces").iterdir()):
                        for ft in file_types:
                            fpath = ws_dir / ft
                            if fpath.exists():
                                with st.expander(f"{ws_dir.name}/{ft}"):
                                    st.code(fpath.read_text(), language="markdown")

                    for shared_file in ["coordination_rules.md", "org_memory.md"]:
                        spath = out_path / "shared" / shared_file
                        if spath.exists():
                            with st.expander(f"shared/{shared_file}"):
                                st.code(spath.read_text(), language="markdown")

                    openclaw_json = (out_path / "openclaw.json").read_text()
                    with st.expander("openclaw.json (with fallbacks + agent-to-agent)"):
                        st.code(openclaw_json, language="json")

                    install_sh = (out_path / "install.sh").read_text()
                    with st.expander("install.sh (phased rollout)"):
                        st.code(install_sh, language="bash")

                    st.download_button(
                        "Download openclaw.json",
                        data=openclaw_json,
                        file_name="openclaw.json",
                        mime="application/json",
                    )
