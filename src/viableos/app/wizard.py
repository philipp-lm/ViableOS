"""5-step setup wizard for ViableOS."""

from __future__ import annotations

import streamlit as st

from viableos.app.components import nav_buttons, step_header, unit_card
from viableos.app.state import (
    TEMPLATE_INFO,
    get_config,
    get_vs,
    load_template,
    set_config,
)

TOTAL_STEPS = 5


def _go(step: int) -> None:
    st.session_state["wizard_step"] = step


def render_wizard() -> None:
    """Main wizard renderer — dispatches to the current step."""
    step = st.session_state.get("wizard_step", 0)
    steps = [_step_identity, _step_template, _step_customize, _step_budget, _step_hitl]

    if 0 <= step < len(steps):
        steps[step]()


# ── Step 0: Identity ────────────────────────────────────────────────────────

def _step_identity() -> None:
    step_header(0, TOTAL_STEPS, "Your Organization",
                "Tell us about your business. This shapes everything.")

    vs = get_vs()

    name = st.text_input(
        "What's the name of your organization?",
        value=vs.get("name", ""),
        placeholder="e.g. My SaaS Startup",
    )

    purpose = st.text_area(
        "What does your organization do? (one or two sentences)",
        value=vs.get("identity", {}).get("purpose", ""),
        placeholder="e.g. We build project management software for remote teams",
        height=100,
    )

    values_default = vs.get("identity", {}).get("values", [])
    values_str = st.text_area(
        "What are your core values? (one per line)",
        value="\n".join(values_default) if values_default else "",
        placeholder="Ship fast, fix fast\nUser experience above technical elegance",
        height=100,
    )
    values = [v.strip() for v in values_str.split("\n") if v.strip()]

    can_proceed = bool(name and purpose)

    back, nxt = nav_buttons(0, TOTAL_STEPS, can_proceed=can_proceed)
    if nxt and can_proceed:
        config = get_config()
        if "viable_system" not in config:
            config["viable_system"] = {}
        config["viable_system"]["name"] = name
        config["viable_system"]["runtime"] = "openclaw"
        if "identity" not in config["viable_system"]:
            config["viable_system"]["identity"] = {}
        config["viable_system"]["identity"]["purpose"] = purpose
        if values:
            config["viable_system"]["identity"]["values"] = values
        set_config(config)
        _go(1)
        st.rerun()


# ── Step 1: Template ────────────────────────────────────────────────────────

def _step_template() -> None:
    step_header(1, TOTAL_STEPS, "Choose a Starting Template",
                "Pick the template closest to your situation. You'll customize it next.")

    cols = st.columns(3)
    selected = st.session_state.get("template_key")

    for i, (key, info) in enumerate(TEMPLATE_INFO.items()):
        col = cols[i % 3]
        with col:
            is_selected = selected == key
            border = "border: 2px solid #6366f1;" if is_selected else "border: 1px solid #334155;"

            st.markdown(
                f"""<div style="padding: 16px; border-radius: 12px; {border}
                margin-bottom: 12px; background: #1e293b;">
                <div style="font-size: 28px; text-align: center; margin-bottom: 8px;">
                    :{info['icon']}:
                </div>
                <div style="font-weight: 700; text-align: center; color: #f8fafc;">
                    {info['name']}
                </div>
                <div style="font-size: 12px; color: #94a3b8; text-align: center; margin-top: 4px;">
                    {info['description']}<br>{info['units']} units
                </div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(
                "Select" if not is_selected else ":white_check_mark: Selected",
                key=f"tpl_{key}",
                use_container_width=True,
            ):
                st.session_state["template_key"] = key
                template_config = load_template(key)
                current = get_config()
                name = current.get("viable_system", {}).get("name", "")
                purpose = current.get("viable_system", {}).get("identity", {}).get("purpose", "")
                values = current.get("viable_system", {}).get("identity", {}).get("values", [])

                template_config["viable_system"]["name"] = name or template_config["viable_system"]["name"]
                template_config["viable_system"]["identity"]["purpose"] = purpose or template_config["viable_system"]["identity"]["purpose"]
                if values:
                    template_config["viable_system"]["identity"]["values"] = values
                set_config(template_config)
                st.rerun()

    back, nxt = nav_buttons(1, TOTAL_STEPS, can_proceed=selected is not None)
    if back:
        _go(0)
        st.rerun()
    if nxt and selected:
        _go(2)
        st.rerun()


# ── Step 2: Customize Units ────────────────────────────────────────────────

def _step_customize() -> None:
    step_header(2, TOTAL_STEPS, "Customize Your Teams",
                "These are your operational units — the agents that do the actual work. "
                "Edit names, purposes, and what they can do alone.")

    config = get_config()
    vs = config.get("viable_system", {})
    units = vs.get("system_1", [])

    edited_units = []
    for i, unit in enumerate(units):
        edited = unit_card(unit, i)
        edited_units.append(edited)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button(":heavy_plus_sign: Add a unit"):
            units.append({"name": "", "purpose": "", "autonomy": "", "tools": []})
            config["viable_system"]["system_1"] = units
            set_config(config)
            st.rerun()
    with col2:
        if len(units) > 1 and st.button(":heavy_minus_sign: Remove last unit"):
            units.pop()
            config["viable_system"]["system_1"] = units
            set_config(config)
            st.rerun()

    has_valid_units = all(u.get("name") and u.get("purpose") for u in edited_units)

    back, nxt = nav_buttons(2, TOTAL_STEPS, can_proceed=has_valid_units)
    if back:
        _go(1)
        st.rerun()
    if nxt and has_valid_units:
        config["viable_system"]["system_1"] = edited_units
        set_config(config)
        _go(3)
        st.rerun()


# ── Step 3: Budget & Models ────────────────────────────────────────────────

def _step_budget() -> None:
    step_header(3, TOTAL_STEPS, "Budget & AI Models",
                "Set your monthly token budget and choose a strategy. "
                "This determines which AI models your agents use.")

    config = get_config()
    vs = config.get("viable_system", {})
    budget = vs.get("budget", {})
    routing = vs.get("model_routing", {})

    monthly = st.slider(
        "Monthly budget (USD)",
        min_value=10,
        max_value=1000,
        value=int(budget.get("monthly_usd", 150)),
        step=10,
        help="How much you want to spend on AI model calls per month",
    )

    st.markdown("#### Strategy")
    strategy_options = {
        "frugal": ":seedling: **Frugal** — Cheapest models everywhere. Best for testing or low-volume.",
        "balanced": ":scales: **Balanced** — Smart routing: cheap for routine, powerful for strategy. Recommended.",
        "performance": ":zap: **Performance** — Best models everywhere. Maximum quality, higher cost.",
    }
    strategy = st.radio(
        "Pick a strategy",
        options=list(strategy_options.keys()),
        format_func=lambda x: strategy_options[x],
        index=["frugal", "balanced", "performance"].index(budget.get("strategy", "balanced")),
        label_visibility="collapsed",
    )

    st.markdown("#### Provider preference")
    provider = st.selectbox(
        "Preferred AI provider",
        options=["anthropic", "openai", "mixed", "ollama"],
        index=["anthropic", "openai", "mixed", "ollama"].index(
            routing.get("provider_preference", "anthropic")
        ),
        help="Anthropic (Claude) is recommended. OpenAI (GPT) also works. Ollama for local models.",
    )

    st.divider()
    st.markdown("#### Budget alerts")
    col1, col2 = st.columns(2)
    with col1:
        warn_pct = st.number_input("Warn at %", value=80, min_value=10, max_value=100, step=5)
    with col2:
        limit_pct = st.number_input("Auto-downgrade at %", value=95, min_value=50, max_value=100, step=5)

    # Preview
    from viableos.budget import calculate_budget

    preview_config = dict(config)
    preview_config.setdefault("viable_system", {})
    preview_config["viable_system"]["budget"] = {"monthly_usd": monthly, "strategy": strategy}
    preview_config["viable_system"]["model_routing"] = {"provider_preference": provider}

    plan = calculate_budget(preview_config)

    st.markdown("#### Preview: How your budget is distributed")
    for alloc in plan.allocations:
        st.markdown(
            f"- **{alloc.system}** — `{alloc.model}` — ${alloc.monthly_usd:.0f}/mo ({alloc.percentage:.0f}%)"
        )

    back, nxt = nav_buttons(3, TOTAL_STEPS)
    if back:
        _go(2)
        st.rerun()
    if nxt:
        config["viable_system"]["budget"] = {
            "monthly_usd": monthly,
            "strategy": strategy,
            "alerts": [
                {"at_percent": warn_pct, "action": "notify"},
                {"at_percent": limit_pct, "action": "downgrade_models"},
            ],
        }
        config["viable_system"]["model_routing"] = {"provider_preference": provider}
        set_config(config)
        _go(4)
        st.rerun()


# ── Step 4: Human-in-the-Loop ──────────────────────────────────────────────

def _step_hitl() -> None:
    step_header(4, TOTAL_STEPS, "Human-in-the-Loop",
                "Decide when agents should ask YOU before acting. "
                "This is the most important safety configuration.")

    config = get_config()
    vs = config.get("viable_system", {})
    hitl = vs.get("human_in_the_loop", {})

    st.markdown("#### How should agents reach you?")
    channel = st.selectbox(
        "Notification channel",
        options=["whatsapp", "telegram", "email", "slack", "discord"],
        index=["whatsapp", "telegram", "email", "slack", "discord"].index(
            hitl.get("notification_channel", "whatsapp")
        ),
    )

    st.markdown("#### What ALWAYS needs your approval?")
    st.caption("Agents will stop and wait for your OK before doing these things.")
    approval_defaults = hitl.get("approval_required", ["deployments", "publishing", "customer_data_access"])
    approval_str = st.text_area(
        "Approval required (one per line)",
        value="\n".join(approval_defaults),
        height=100,
        label_visibility="collapsed",
    )
    approval = [a.strip() for a in approval_str.split("\n") if a.strip()]

    st.markdown("#### What should agents send for your review?")
    st.caption("Agents can proceed, but they'll share results for you to check.")
    review_defaults = hitl.get("review_required", ["feature_implementations", "content_drafts"])
    review_str = st.text_area(
        "Review required (one per line)",
        value="\n".join(review_defaults),
        height=80,
        label_visibility="collapsed",
    )
    review = [r.strip() for r in review_str.split("\n") if r.strip()]

    st.markdown("#### Emergency alerts")
    st.caption("These interrupt you immediately, no matter what.")
    emergency_defaults = hitl.get("emergency_alerts", ["data_leak", "security_vulnerability", "budget_exceeded_95"])
    emergency_str = st.text_area(
        "Emergency alerts (one per line)",
        value="\n".join(emergency_defaults),
        height=80,
        label_visibility="collapsed",
    )
    emergency = [e.strip() for e in emergency_str.split("\n") if e.strip()]

    st.divider()
    identity = vs.get("identity", {})
    human_decisions = identity.get("decisions_requiring_human", [])
    st.markdown("#### Decisions requiring the human (from identity)")
    st.caption("These are set in Step 1 and enforced by the Policy Guardian (S5).")
    for d in human_decisions:
        st.markdown(f"- {d}")
    if not human_decisions:
        st.info("No identity-level decision gates set. Consider adding some in your config.")

    back, nxt = nav_buttons(4, TOTAL_STEPS)
    if back:
        _go(3)
        st.rerun()
    if nxt:
        config["viable_system"]["human_in_the_loop"] = {
            "notification_channel": channel,
            "approval_required": approval,
            "review_required": review,
            "emergency_alerts": emergency,
        }
        set_config(config)
        st.session_state["view"] = "dashboard"
        st.rerun()
