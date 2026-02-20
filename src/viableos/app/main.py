"""ViableOS — The operating system for viable AI agent organizations.

Entry point for the Streamlit web app.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="ViableOS",
    page_icon=":shield:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject global dark theme overrides
st.markdown(
    """<style>
    .stApp { background-color: #0f172a; }
    .stMetric label { color: #94a3b8 !important; }
    .stMetric [data-testid="stMetricValue"] { color: #f8fafc !important; }
    section[data-testid="stSidebar"] { background-color: #1e293b; }
    .stSelectbox label, .stTextInput label, .stTextArea label,
    .stRadio label, .stSlider label, .stNumberInput label { color: #cbd5e1 !important; }
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
    </style>""",
    unsafe_allow_html=True,
)

from viableos.app.dashboard import render_dashboard  # noqa: E402
from viableos.app.state import init_state, load_template, set_config  # noqa: E402
from viableos.app.wizard import render_wizard  # noqa: E402

init_state()


def _sidebar() -> None:
    """Render the sidebar with navigation and demo mode."""
    with st.sidebar:
        st.markdown("## :shield: ViableOS")
        st.caption("v0.2.0")
        st.divider()

        view = st.session_state.get("view", "wizard")

        if st.button(
            ":magic_wand: Setup Wizard",
            use_container_width=True,
            type="primary" if view == "wizard" else "secondary",
        ):
            st.session_state["view"] = "wizard"
            st.rerun()

        if st.button(
            ":bar_chart: Dashboard",
            use_container_width=True,
            type="primary" if view == "dashboard" else "secondary",
        ):
            st.session_state["view"] = "dashboard"
            st.rerun()

        st.divider()

        st.markdown("#### Quick Start")
        if st.button(":rocket: Demo: SaaS Startup", use_container_width=True):
            _load_demo("saas-startup")
        if st.button(":shopping_bags: Demo: E-Commerce", use_container_width=True):
            _load_demo("ecommerce")
        if st.button(":briefcase: Demo: Freelancer", use_container_width=True):
            _load_demo("freelance-agency")
        if st.button(":art: Demo: Content Creator", use_container_width=True):
            _load_demo("content-creator")
        if st.button(":brain: Demo: Productivity", use_container_width=True):
            _load_demo("personal-productivity")

        st.divider()
        if st.button(":arrows_counterclockwise: Reset Everything", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
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
        st.markdown("# :shield: ViableOS Setup")
        st.markdown(
            "Build your AI agent organization in 5 steps. "
            "Based on the *Viable System Model* — the management framework that makes organizations self-governing."
        )
        st.divider()
        render_wizard()
    elif view == "dashboard":
        render_dashboard()


main()
