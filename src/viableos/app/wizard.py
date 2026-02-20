"""5-step setup wizard for ViableOS.

Step order: Template -> Identity -> Customize Units -> Budget & Models -> Human-in-the-Loop
"""

from __future__ import annotations

import streamlit as st

from viableos.app.components import multi_select_chips, nav_buttons, step_header, unit_editor
from viableos.app.state import (
    APPROVAL_PRESETS,
    AUTONOMY_LEVELS,
    EMERGENCY_PRESETS,
    NOTIFICATION_CHANNELS,
    REVIEW_PRESETS,
    TEMPLATE_INFO,
    TOOL_CATEGORIES,
    VALUE_PRESETS,
    get_config,
    get_vs,
    load_template,
    set_config,
)
from viableos.budget import MODEL_CATALOG, calculate_budget, get_all_models

TOTAL_STEPS = 5


def _go(step: int) -> None:
    st.session_state["wizard_step"] = step


def render_wizard() -> None:
    """Main wizard renderer — dispatches to the current step."""
    step = st.session_state.get("wizard_step", 0)
    steps = [_step_template, _step_identity, _step_customize, _step_budget, _step_hitl]

    if 0 <= step < len(steps):
        steps[step]()


# ── Step 0: Choose a Template ────────────────────────────────────────────────

def _step_template() -> None:
    step_header(0, TOTAL_STEPS, "Choose Your Starting Point",
                "Pick a template to pre-fill your setup, or start from scratch.")

    selected = st.session_state.get("template_key")

    cols = st.columns(4)
    for i, (key, info) in enumerate(TEMPLATE_INFO.items()):
        col = cols[i % 4]
        with col:
            is_selected = selected == key
            border_color = "#6366f1" if is_selected else "#334155"
            check = " [selected]" if is_selected else ""
            is_custom = key == "custom"

            bg = "#1a1a3e" if is_custom else "#1e293b"

            st.markdown(
                f"""<div style="padding: 14px; border-radius: 10px;
                border: 2px solid {border_color};
                margin-bottom: 10px; background: {bg};">
                <div style="font-weight: 700; color: #f8fafc; font-size: 14px;">
                    {info['name']}{check}
                </div>
                <div style="font-size: 11px; color: #94a3b8; margin: 4px 0;">
                    {info['tagline']}
                </div>
                <div style="font-size: 11px; color: #64748b;">
                    {info['description']}{f" | {info['units']} units" if info['units'] else ''}
                </div>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(
                "Selected" if is_selected else "Select",
                key=f"tpl_{key}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state["template_key"] = key
                if key == "custom":
                    config = get_config()
                    if "viable_system" not in config:
                        config["viable_system"] = {
                            "name": "",
                            "runtime": "openclaw",
                            "identity": {"purpose": ""},
                            "system_1": [{"name": "", "purpose": "", "autonomy": "", "tools": []}],
                            "budget": {"monthly_usd": 150, "strategy": "balanced"},
                        }
                    set_config(config)
                else:
                    template_config = load_template(key)
                    current = get_config()
                    name = current.get("viable_system", {}).get("name", "")
                    purpose = current.get("viable_system", {}).get("identity", {}).get("purpose", "")
                    if template_config:
                        if name:
                            template_config["viable_system"]["name"] = name
                        if purpose:
                            template_config["viable_system"]["identity"]["purpose"] = purpose
                        set_config(template_config)
                st.rerun()

    back, nxt = nav_buttons(0, TOTAL_STEPS, can_proceed=selected is not None)
    if nxt and selected:
        _go(1)
        st.rerun()


# ── Step 1: Identity ────────────────────────────────────────────────────────

def _step_identity() -> None:
    step_header(1, TOTAL_STEPS, "Your Organization",
                "Name your system, describe its purpose, and pick the values that guide your agents.")

    vs = get_vs()

    name = st.text_input(
        "Organization name",
        value=vs.get("name", ""),
        placeholder="e.g. My SaaS Startup",
    )

    purpose = st.text_area(
        "What does your organization do? (1-2 sentences)",
        value=vs.get("identity", {}).get("purpose", ""),
        placeholder="e.g. We build project management software for remote teams",
        height=80,
    )

    st.markdown("**Core values** — pick from the list, or add your own below")

    existing_values = vs.get("identity", {}).get("values", [])
    known_selected = [v for v in existing_values if v in VALUE_PRESETS]
    custom_existing = [v for v in existing_values if v not in VALUE_PRESETS]

    selected_values = multi_select_chips(
        "Select values",
        options=VALUE_PRESETS,
        default=known_selected,
        key="identity_values",
    )

    custom_values_str = st.text_input(
        "Additional values (comma-separated)",
        value=", ".join(custom_existing),
        placeholder="e.g. Move fast and learn, Respect everyone's time",
    )
    custom_values = [v.strip() for v in custom_values_str.split(",") if v.strip()] if custom_values_str else []

    all_values = selected_values + [v for v in custom_values if v not in selected_values]

    can_proceed = bool(name and purpose)

    back, nxt = nav_buttons(1, TOTAL_STEPS, can_proceed=can_proceed)
    if back:
        _go(0)
        st.rerun()
    if nxt and can_proceed:
        config = get_config()
        config.setdefault("viable_system", {})
        config["viable_system"]["name"] = name
        config["viable_system"]["runtime"] = "openclaw"
        config["viable_system"].setdefault("identity", {})
        config["viable_system"]["identity"]["purpose"] = purpose
        if all_values:
            config["viable_system"]["identity"]["values"] = all_values
        set_config(config)
        _go(2)
        st.rerun()


# ── Step 2: Customize Units ────────────────────────────────────────────────

def _step_customize() -> None:
    step_header(2, TOTAL_STEPS, "Customize Your Teams",
                "These are your operational units — the agents that do the actual work. "
                "Adjust names, purposes, autonomy levels, and tools.")

    config = get_config()
    vs = config.get("viable_system", {})
    units = vs.get("system_1", [])

    if not units:
        units = [{"name": "", "purpose": "", "autonomy": "", "tools": []}]
        config["viable_system"]["system_1"] = units
        set_config(config)

    edited_units = []
    for i, unit in enumerate(units):
        edited = unit_editor(unit, i, AUTONOMY_LEVELS, TOOL_CATEGORIES)
        edited_units.append(edited)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("+ Add a unit"):
            units.append({"name": "", "purpose": "", "autonomy": "", "tools": []})
            config["viable_system"]["system_1"] = units
            set_config(config)
            st.rerun()
    with col2:
        if len(units) > 1 and st.button("- Remove last unit"):
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
                "Set your budget, choose models per unit, and see how it all distributes.")

    config = get_config()
    vs = config.get("viable_system", {})
    budget = vs.get("budget", {})
    routing = vs.get("model_routing", {})
    units = vs.get("system_1", [])

    all_models = get_all_models()

    # Global settings
    st.markdown("#### Global settings")

    col_budget, col_strategy = st.columns(2)
    with col_budget:
        monthly = st.slider(
            "Monthly budget (USD)",
            min_value=10,
            max_value=1000,
            value=int(budget.get("monthly_usd", 150)),
            step=10,
        )
    with col_strategy:
        strategy_labels = {
            "frugal": "Frugal — cheapest models, good for testing",
            "balanced": "Balanced — smart routing, recommended",
            "performance": "Performance — best models everywhere",
        }
        strategy = st.radio(
            "Strategy",
            options=["frugal", "balanced", "performance"],
            format_func=lambda x: strategy_labels[x],
            index=["frugal", "balanced", "performance"].index(budget.get("strategy", "balanced")),
        )

    st.markdown("#### Default provider")
    provider_labels = {
        "anthropic": "Anthropic (Claude)",
        "openai": "OpenAI (GPT, Codex, o3)",
        "google": "Google (Gemini)",
        "deepseek": "DeepSeek",
        "xai": "xAI (Grok)",
        "meta": "Meta (Llama)",
        "mixed": "Mixed (pick per unit)",
        "ollama": "Ollama (local models)",
    }
    provider_keys = list(provider_labels.keys())
    current_provider = routing.get("provider_preference", "anthropic")
    provider = st.radio(
        "Default provider",
        options=provider_keys,
        format_func=lambda x: provider_labels[x],
        index=provider_keys.index(current_provider) if current_provider in provider_keys else 0,
        horizontal=True,
        label_visibility="collapsed",
    )

    # Per-unit customization
    st.divider()
    st.markdown("#### Per-unit model & weight")
    st.caption("Pick a specific model for each unit and set its budget weight. "
               "Higher weight = larger share of the S1 budget (65% of total).")

    updated_units = []
    for i, unit in enumerate(units):
        uname = unit.get("name", f"Unit {i+1}")
        current_model = unit.get("model", "")
        current_weight = unit.get("weight", 5)

        with st.expander(f"**{uname}** — {unit.get('purpose', '')[:50]}", expanded=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                model_options = ["(auto — use strategy default)"] + all_models
                default_idx = 0
                if current_model and current_model in all_models:
                    default_idx = all_models.index(current_model) + 1

                selected_model = st.selectbox(
                    f"Model for {uname}",
                    options=model_options,
                    index=default_idx,
                    key=f"unit_model_{i}",
                    label_visibility="collapsed",
                )
                if selected_model != "(auto — use strategy default)":
                    info = MODEL_CATALOG.get(selected_model, {})
                    st.caption(f"{info.get('tier', '').title()} — {info.get('note', '')}")

            with c2:
                weight = st.slider(
                    "Weight",
                    min_value=1,
                    max_value=10,
                    value=int(current_weight),
                    key=f"unit_weight_{i}",
                    label_visibility="collapsed",
                )

            unit_copy = dict(unit)
            if selected_model and selected_model != "(auto — use strategy default)":
                unit_copy["model"] = selected_model
            elif "model" in unit_copy:
                del unit_copy["model"]
            unit_copy["weight"] = weight
            updated_units.append(unit_copy)

    # Budget alerts
    st.divider()
    st.markdown("#### Budget alerts")
    col_warn, col_limit = st.columns(2)
    with col_warn:
        warn_pct = st.number_input("Warn at %", value=80, min_value=10, max_value=100, step=5)
    with col_limit:
        limit_pct = st.number_input("Auto-downgrade at %", value=95, min_value=50, max_value=100, step=5)

    # Live preview using the ACTUAL unit settings
    st.divider()
    st.markdown("#### Budget preview (live)")

    preview_config = {
        "viable_system": {
            **vs,
            "system_1": updated_units,
            "budget": {"monthly_usd": monthly, "strategy": strategy},
            "model_routing": {"provider_preference": provider},
        }
    }
    plan = calculate_budget(preview_config)

    for alloc in plan.allocations:
        pct_bar = int(alloc.percentage / 2)
        bar = "█" * pct_bar + "░" * (50 - pct_bar)
        model_short = alloc.model.split("/")[-1] if "/" in alloc.model else alloc.model
        st.text(f"  {alloc.system:<20} {bar} ${alloc.monthly_usd:>5.0f}/mo  {model_short}")

    back, nxt = nav_buttons(3, TOTAL_STEPS)
    if back:
        _go(2)
        st.rerun()
    if nxt:
        config["viable_system"]["system_1"] = updated_units
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
                "The most important safety config: decide when agents must ask YOU before acting.")

    config = get_config()
    vs = config.get("viable_system", {})
    hitl = vs.get("human_in_the_loop", {})

    # Notification channel
    st.markdown("#### How should agents reach you?")
    current_channel = hitl.get("notification_channel", "whatsapp")
    channel = st.radio(
        "Notification channel",
        options=NOTIFICATION_CHANNELS,
        index=NOTIFICATION_CHANNELS.index(current_channel) if current_channel in NOTIFICATION_CHANNELS else 0,
        horizontal=True,
        label_visibility="collapsed",
    )

    # Approval required
    st.divider()
    st.markdown("#### Needs your approval")
    st.caption("Agents will **stop and wait** for your OK before doing these things.")

    existing_approval = hitl.get("approval_required", [])
    default_approval = [p for p in APPROVAL_PRESETS if any(
        p.lower().replace(" ", "_") == a.lower().replace(" ", "_") or p == a
        for a in existing_approval
    )] or APPROVAL_PRESETS[:3]

    approval_selected = st.multiselect(
        "Select approval items",
        options=APPROVAL_PRESETS,
        default=default_approval,
        key="hitl_approval",
        label_visibility="collapsed",
    )
    approval_custom = st.text_input(
        "Additional approval items (comma-separated)",
        key="hitl_approval_custom",
        placeholder="e.g. database migrations, API key rotations",
    )
    extra_approval = [a.strip() for a in approval_custom.split(",") if a.strip()] if approval_custom else []
    all_approval = approval_selected + extra_approval

    # Review required
    st.divider()
    st.markdown("#### Sent for your review")
    st.caption("Agents can proceed, but they will share results for you to check.")

    existing_review = hitl.get("review_required", [])
    default_review = [p for p in REVIEW_PRESETS if any(
        p.lower().replace(" ", "_") == r.lower().replace(" ", "_") or p == r
        for r in existing_review
    )] or REVIEW_PRESETS[:2]

    review_selected = st.multiselect(
        "Select review items",
        options=REVIEW_PRESETS,
        default=default_review,
        key="hitl_review",
        label_visibility="collapsed",
    )
    review_custom = st.text_input(
        "Additional review items (comma-separated)",
        key="hitl_review_custom",
        placeholder="e.g. partner contracts, investor updates",
    )
    extra_review = [r.strip() for r in review_custom.split(",") if r.strip()] if review_custom else []
    all_review = review_selected + extra_review

    # Emergency alerts
    st.divider()
    st.markdown("#### Emergency alerts")
    st.caption("These **interrupt you immediately**, no matter what.")

    existing_emergency = hitl.get("emergency_alerts", [])
    default_emergency = [p for p in EMERGENCY_PRESETS if any(
        p.lower().replace(" ", "_") == e.lower().replace(" ", "_") or p == e
        for e in existing_emergency
    )] or EMERGENCY_PRESETS[:3]

    emergency_selected = st.multiselect(
        "Select emergency items",
        options=EMERGENCY_PRESETS,
        default=default_emergency,
        key="hitl_emergency",
        label_visibility="collapsed",
    )
    emergency_custom = st.text_input(
        "Additional emergency items (comma-separated)",
        key="hitl_emergency_custom",
        placeholder="e.g. failed payment processing",
    )
    extra_emergency = [e.strip() for e in emergency_custom.split(",") if e.strip()] if emergency_custom else []
    all_emergency = emergency_selected + extra_emergency

    back, nxt = nav_buttons(4, TOTAL_STEPS)
    if back:
        _go(3)
        st.rerun()
    if nxt:
        config["viable_system"]["human_in_the_loop"] = {
            "notification_channel": channel,
            "approval_required": all_approval,
            "review_required": all_review,
            "emergency_alerts": all_emergency,
        }
        set_config(config)
        st.session_state["view"] = "dashboard"
        st.rerun()
