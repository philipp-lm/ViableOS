"""ViableOS — The operating system for viable AI agent organizations.

Entry point for the Streamlit web app.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="ViableOS",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color: #0f172a; font-family: 'Inter', sans-serif; }
    .stMetric label { color: #94a3b8 !important; }
    .stMetric [data-testid="stMetricValue"] { color: #f8fafc !important; }
    section[data-testid="stSidebar"] { background-color: #1e293b; }
    .stSelectbox label, .stTextInput label, .stTextArea label,
    .stRadio label, .stSlider label, .stNumberInput label,
    .stMultiSelect label { color: #cbd5e1 !important; }
    h1, h2, h3, h4, h5 { color: #f8fafc !important; }
    p, li, span { color: #cbd5e1; }
    .stDivider { border-color: #334155 !important; }
    div[data-testid="stExpander"] { border-color: #334155 !important; }
    .stButton > button[kind="primary"] {
        background-color: #6366f1 !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4f46e5 !important;
    }
    .stProgress > div > div { background-color: #6366f1 !important; }
    </style>""",
    unsafe_allow_html=True,
)

from viableos.app.dashboard import render_dashboard  # noqa: E402
from viableos.app.state import TEMPLATE_INFO, init_state, load_template, set_config  # noqa: E402
from viableos.app.wizard import render_wizard  # noqa: E402

init_state()


def _sidebar() -> None:
    """Render the sidebar with navigation and demo mode."""
    with st.sidebar:
        st.markdown("## ViableOS")
        st.caption("v0.2.0")
        st.divider()

        view = st.session_state.get("view", "wizard")

        if st.button(
            "Setup Wizard",
            use_container_width=True,
            type="primary" if view == "wizard" else "secondary",
        ):
            st.session_state["view"] = "wizard"
            st.rerun()

        if st.button(
            "Dashboard",
            use_container_width=True,
            type="primary" if view == "dashboard" else "secondary",
        ):
            st.session_state["view"] = "dashboard"
            st.rerun()

        st.divider()
        st.markdown("#### Quick demos")
        st.caption("Load a fully configured system instantly.")

        for key, info in TEMPLATE_INFO.items():
            if key == "custom":
                continue
            if st.button(f"{info['name']}", key=f"demo_{key}", use_container_width=True):
                _load_demo(key)

        st.divider()
        if st.button("Reset everything", use_container_width=True):
            for skey in list(st.session_state.keys()):
                del st.session_state[skey]
            st.rerun()


def _load_demo(template_key: str) -> None:
    config = load_template(template_key)
    if config:
        set_config(config)
        st.session_state["template_key"] = template_key
        st.session_state["view"] = "dashboard"
        st.rerun()


def main() -> None:
    _sidebar()
    view = st.session_state.get("view", "wizard")

    if view == "wizard":
        st.markdown("# ViableOS Setup")
        st.markdown(
            "Build your AI agent organization in 5 steps. "
            "Based on the Viable System Model — the management framework "
            "that makes organizations self-governing."
        )
        st.divider()
        render_wizard()
    elif view == "dashboard":
        render_dashboard()


main()
