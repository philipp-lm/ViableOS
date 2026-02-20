"""Reusable UI components for the ViableOS web app."""

from __future__ import annotations

from typing import Any

import streamlit as st


def step_header(step: int, total: int, title: str, subtitle: str = "") -> None:
    """Render a wizard step header with progress dots."""
    dots = ""
    for i in range(total):
        if i < step:
            dots += " :white_check_mark: "
        elif i == step:
            dots += " :large_blue_circle: "
        else:
            dots += " :white_circle: "

    st.markdown(f"### Step {step + 1} of {total}: {title}")
    st.markdown(dots)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def nav_buttons(
    step: int,
    total: int,
    on_next: str = "Next",
    can_proceed: bool = True,
) -> tuple[bool, bool]:
    """Render back/next navigation. Returns (back_clicked, next_clicked)."""
    cols = st.columns([1, 3, 1])
    back = False
    nxt = False

    with cols[0]:
        if step > 0:
            back = st.button(":arrow_left: Back", use_container_width=True)

    with cols[2]:
        if step < total - 1:
            nxt = st.button(
                f"{on_next} :arrow_right:",
                use_container_width=True,
                disabled=not can_proceed,
                type="primary",
            )
        else:
            nxt = st.button(
                ":white_check_mark: Generate",
                use_container_width=True,
                disabled=not can_proceed,
                type="primary",
            )

    return back, nxt


def info_card(title: str, value: str, icon: str = "") -> None:
    """Render a metric-style info card."""
    prefix = f":{icon}: " if icon else ""
    st.metric(label=f"{prefix}{title}", value=value)


def unit_card(unit: dict[str, Any], index: int) -> dict[str, Any]:
    """Render an editable S1 unit card. Returns the (possibly edited) unit."""
    with st.expander(f":gear: **{unit.get('name', f'Unit {index + 1}')}**", expanded=True):
        name = st.text_input("Name", value=unit.get("name", ""), key=f"unit_name_{index}")
        purpose = st.text_input("Purpose", value=unit.get("purpose", ""), key=f"unit_purpose_{index}")
        autonomy = st.text_area(
            "Autonomy (what can this agent do without asking?)",
            value=unit.get("autonomy", ""),
            key=f"unit_autonomy_{index}",
            height=68,
        )
        tools_str = ", ".join(unit.get("tools", []))
        tools_input = st.text_input(
            "Tools (comma-separated)",
            value=tools_str,
            key=f"unit_tools_{index}",
        )
        tools = [t.strip() for t in tools_input.split(",") if t.strip()] if tools_input else []

        return {
            "name": name,
            "purpose": purpose,
            "autonomy": autonomy,
            "tools": tools,
        }


def vsm_system_badge(system: str, name: str, present: bool) -> None:
    """Render a VSM system status badge."""
    icon = ":white_check_mark:" if present else ":x:"
    st.markdown(f"{icon} **{system}** — {name}")
