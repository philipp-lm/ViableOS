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

_AUTO = "(auto — use strategy default)"

SYSTEM_MODEL_KEYS = {
    "S2 Coordinator": "s2_coordination",
    "S3 Optimizer": "s3_optimization",
    "S3* Auditor": "s3_star_audit",
    "S4 Scout": "s4_intelligence",
    "S5 Policy Guardian": "s5_preparation",
}

SYSTEM_DESCRIPTIONS = {
    "S2 Coordinator": "Prevents conflicts between operational units — lightweight, needs speed",
    "S3 Optimizer": "Manages resources, creates weekly digest — needs analytical power",
    "S3* Auditor": "Independent quality checks — should use different provider than S1",
    "S4 Scout": "Monitors environment, strategic briefs — needs strong reasoning",
    "S5 Policy Guardian": "Enforces values, prepares human decisions — needs precision",
}


def _model_selector(label: str, current: str, all_models: list[str], key: str) -> str:
    """Reusable model selectbox with auto option. Returns model ID or empty string."""
    options = [_AUTO] + all_models
    idx = 0
    if current and current in all_models:
        idx = all_models.index(current) + 1
    selected = st.selectbox(label, options=options, index=idx, key=key, label_visibility="collapsed")
    if selected != _AUTO:
        info = MODEL_CATALOG.get(selected, {})
        st.caption(f"{info.get('tier', '').title()} — {info.get('note', '')}")
        return selected
    return ""


def _step_budget() -> None:
    step_header(3, TOTAL_STEPS, "Budget & AI Models",
                "Set your budget and choose models for every system. "
                "Expand each section to override the strategy default.")

    config = get_config()
    vs = config.get("viable_system", {})
    budget = vs.get("budget", {})
    routing = vs.get("model_routing", {})
    units = vs.get("system_1", [])

    all_models = get_all_models()

    # ── Global settings ──────────────────────────────────────────────────
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
        "openai": "OpenAI (GPT-5.x, Codex, o3)",
        "google": "Google (Gemini)",
        "deepseek": "DeepSeek",
        "xai": "xAI (Grok)",
        "meta": "Meta (Llama)",
        "mixed": "Mixed (pick per system)",
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

    # ── S1: Per-unit model & weight ──────────────────────────────────────
    st.divider()
    st.markdown("#### S1 — Operational Units (65% of budget)")
    st.caption("Pick a model and budget weight for each unit.")

    updated_units = []
    for i, unit in enumerate(units):
        uname = unit.get("name", f"Unit {i+1}")
        current_model = unit.get("model", "")
        current_weight = unit.get("weight", 5)

        with st.expander(f"**{uname}** — {unit.get('purpose', '')[:50]}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                sel = _model_selector(f"Model for {uname}", current_model, all_models, f"unit_model_{i}")
            with c2:
                weight = st.slider(
                    "Budget weight",
                    min_value=1,
                    max_value=10,
                    value=int(current_weight),
                    key=f"unit_weight_{i}",
                    label_visibility="collapsed",
                    help="Higher = larger share of S1 budget",
                )

            unit_copy = dict(unit)
            if sel:
                unit_copy["model"] = sel
            elif "model" in unit_copy:
                del unit_copy["model"]
            unit_copy["weight"] = weight
            updated_units.append(unit_copy)

    # ── S2-S5: Per-system model selection ────────────────────────────────
    st.divider()
    st.markdown("#### Management Systems (35% of budget)")
    st.caption("Override the default model for each management system.")

    updated_routing: dict[str, str] = {}

    for sys_label, routing_key in SYSTEM_MODEL_KEYS.items():
        current = routing.get(routing_key, "")
        with st.expander(f"**{sys_label}** — {SYSTEM_DESCRIPTIONS[sys_label]}", expanded=False):
            sel = _model_selector(
                f"Model for {sys_label}",
                current,
                all_models,
                f"sys_model_{routing_key}",
            )
            if sel:
                updated_routing[routing_key] = sel

    # ── Budget alerts ────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### Budget alerts")
    col_warn, col_limit = st.columns(2)
    with col_warn:
        warn_pct = st.number_input("Warn at %", value=80, min_value=10, max_value=100, step=5)
    with col_limit:
        limit_pct = st.number_input("Auto-downgrade at %", value=95, min_value=50, max_value=100, step=5)

    # ── Live preview ─────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### Budget preview (live)")

    preview_routing = {"provider_preference": provider, **updated_routing}
    preview_config = {
        "viable_system": {
            **vs,
            "system_1": updated_units,
            "budget": {"monthly_usd": monthly, "strategy": strategy},
            "model_routing": preview_routing,
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
        config["viable_system"]["model_routing"] = {
            "provider_preference": provider,
            **updated_routing,
        }
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
