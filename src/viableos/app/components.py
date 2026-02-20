"""Reusable UI components for the ViableOS web app."""

from __future__ import annotations

from typing import Any

import streamlit as st


def step_header(step: int, total: int, title: str, subtitle: str = "") -> None:
    """Render a wizard step header with progress bar."""
    progress = (step) / total
    st.progress(progress)
    st.markdown(f"### Step {step + 1} of {total} — {title}")
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
            back = st.button("< Back", use_container_width=True)

    with cols[2]:
        if step < total - 1:
            nxt = st.button(
                f"{on_next} >",
                use_container_width=True,
                disabled=not can_proceed,
                type="primary",
            )
        else:
            nxt = st.button(
                "Generate",
                use_container_width=True,
                disabled=not can_proceed,
                type="primary",
            )

    return back, nxt


def multi_select_chips(
    label: str,
    options: list[str],
    default: list[str] | None = None,
    key: str = "",
    help_text: str = "",
) -> list[str]:
    """Multi-select presented as a multiselect widget."""
    if help_text:
        st.caption(help_text)
    return st.multiselect(
        label,
        options=options,
        default=default or [],
        key=key,
    )


def unit_editor(unit: dict[str, Any], index: int, autonomy_options: dict[str, str], tool_options: dict[str, list[str]]) -> dict[str, Any]:
    """Render an editable S1 unit card with multi-choice for autonomy and tools."""
    with st.expander(f"**{unit.get('name', f'Unit {index + 1}')}**", expanded=True):
        name = st.text_input("Name", value=unit.get("name", ""), key=f"unit_name_{index}")
        purpose = st.text_input("Purpose", value=unit.get("purpose", ""), key=f"unit_purpose_{index}")

        st.markdown("**Autonomy level**")
        current_autonomy = unit.get("autonomy", "")
        autonomy_keys = list(autonomy_options.keys())
        default_idx = 0
        for i, (k, v) in enumerate(autonomy_options.items()):
            if current_autonomy and (k in current_autonomy.lower() or current_autonomy == v):
                default_idx = i
                break

        selected_autonomy = st.radio(
            "Pick an autonomy level",
            options=autonomy_keys,
            format_func=lambda x: autonomy_options[x],
            index=default_idx,
            key=f"unit_autonomy_radio_{index}",
            label_visibility="collapsed",
        )
        autonomy_custom = st.text_input(
            "Customize autonomy (optional)",
            value="" if selected_autonomy else current_autonomy,
            key=f"unit_autonomy_custom_{index}",
            placeholder="Add specifics, e.g. 'Can fix bugs alone, features need approval'",
        )

        st.markdown("**Tools**")
        existing_tools = unit.get("tools", [])
        all_tool_flat = []
        for cat_tools in tool_options.values():
            all_tool_flat.extend(cat_tools)
        pre_selected = [t for t in existing_tools if t in all_tool_flat]

        selected_tools = st.multiselect(
            "Select from common tools",
            options=all_tool_flat,
            default=pre_selected,
            key=f"unit_tools_multi_{index}",
            label_visibility="collapsed",
        )
        extra_tools_str = st.text_input(
            "Additional tools (comma-separated)",
            value=", ".join(t for t in existing_tools if t not in all_tool_flat),
            key=f"unit_tools_extra_{index}",
            placeholder="e.g. custom-api, internal-tool",
        )
        extra_tools = [t.strip() for t in extra_tools_str.split(",") if t.strip()] if extra_tools_str else []

        final_autonomy = autonomy_custom if autonomy_custom else autonomy_options.get(selected_autonomy, "")
        all_tools = selected_tools + [t for t in extra_tools if t not in selected_tools]

        return {
            "name": name,
            "purpose": purpose,
            "autonomy": final_autonomy,
            "tools": all_tools,
        }
