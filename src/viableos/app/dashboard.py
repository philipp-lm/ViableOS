"""Dashboard view — VSM overview, budget, agents, HiTL summary."""

from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st
import yaml

from viableos.app.charts import budget_donut, model_tier_bar, vsm_overview_diagram
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
        st.markdown(f"## :shield: {system_name}")
    with col_actions:
        if st.button(":pencil2: Edit in Wizard"):
            st.session_state["view"] = "wizard"
            st.session_state["wizard_step"] = 0
            st.rerun()

    # Validation status
    errors = validate(config)
    if errors:
        st.error(f"Configuration has {len(errors)} validation errors")
        for err in errors:
            st.markdown(f"- {err}")
        return

    plan = calculate_budget(config)
    report = check_viability(config)

    # ── Top metrics ──────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Viability Score", f"{report.score}/{report.total}")
    with m2:
        st.metric("Monthly Budget", f"${plan.total_monthly_usd:.0f}")
    with m3:
        st.metric("Strategy", plan.strategy.title())
    with m4:
        st.metric("Agents", str(len(plan.allocations)))

    st.divider()

    # ── Two-column layout ────────────────────────────────────────────────
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("### VSM System Map")
        fig = vsm_overview_diagram(config)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### Viability Checklist")
        for check in report.checks:
            icon = ":white_check_mark:" if check.present else ":x:"
            st.markdown(f"{icon} **{check.system} {check.name}** — {check.details}")
            if not check.present:
                for sug in check.suggestions:
                    st.caption(f"  -> {sug}")

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

    # ── Agent cards ──────────────────────────────────────────────────────
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
        })

    cols = st.columns(3)
    for i, agent in enumerate(agent_data):
        with cols[i % 3]:
            st.markdown(
                f"""<div style="padding: 14px; border-radius: 10px;
                border: 1px solid #334155; background: #1e293b; margin-bottom: 12px;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 15px;">
                    {agent['name']}
                </div>
                <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
                    {agent['role']}
                </div>
                <div style="font-size: 12px; color: #cbd5e1; margin-bottom: 4px;">
                    {agent['purpose']}
                </div>
                <div style="font-size: 11px; color: #64748b; margin-top: 6px;">
                    Model: <code>{agent['model'].split('/')[-1]}</code>
                    &nbsp;|&nbsp; Budget: {agent['budget']}/mo
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Human-in-the-Loop summary ────────────────────────────────────────
    hitl = vs.get("human_in_the_loop", {})
    if hitl:
        st.markdown("### Human-in-the-Loop Configuration")
        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown("**:stop_sign: Needs Your Approval**")
            for item in hitl.get("approval_required", []):
                st.markdown(f"- {item}")
        with h2:
            st.markdown("**:eyes: Sent for Review**")
            for item in hitl.get("review_required", []):
                st.markdown(f"- {item}")
        with h3:
            st.markdown("**:rotating_light: Emergency Alerts**")
            for item in hitl.get("emergency_alerts", []):
                st.markdown(f"- {item}")

        st.caption(f"Notification channel: **{hitl.get('notification_channel', 'not set')}**")

    st.divider()

    # ── Export actions ───────────────────────────────────────────────────
    st.markdown("### Export")

    col_yaml, col_generate = st.columns(2)

    with col_yaml:
        yaml_str = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
        st.download_button(
            ":page_facing_up: Download YAML Config",
            data=yaml_str,
            file_name="viableos.yaml",
            mime="text/yaml",
            use_container_width=True,
        )

    with col_generate:
        if st.button(":package: Generate OpenClaw Package", use_container_width=True, type="primary"):
            with st.spinner("Generating..."):
                with tempfile.TemporaryDirectory() as tmp:
                    out_path = generate_openclaw_package(config, Path(tmp) / "viableos-openclaw")
                    agent_count = len(list(out_path.glob("workspaces/*/SOUL.md")))

                    st.session_state["_last_generated_path"] = str(out_path)
                    st.session_state["_last_agent_count"] = agent_count

                    st.success(f"Generated {agent_count} agents!")

                    for ws_dir in sorted((out_path / "workspaces").iterdir()):
                        soul_path = ws_dir / "SOUL.md"
                        if soul_path.exists():
                            with st.expander(f":robot_face: {ws_dir.name}/SOUL.md"):
                                st.code(soul_path.read_text(), language="markdown")

                    openclaw_json = (out_path / "openclaw.json").read_text()
                    with st.expander(":gear: openclaw.json"):
                        st.code(openclaw_json, language="json")

                    st.download_button(
                        ":inbox_tray: Download openclaw.json",
                        data=openclaw_json,
                        file_name="openclaw.json",
                        mime="application/json",
                    )
