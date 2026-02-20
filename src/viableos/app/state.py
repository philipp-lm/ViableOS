"""Session state management for the ViableOS wizard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import yaml

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TEMPLATE_INFO = {
    "saas-startup": {
        "name": "SaaS Startup",
        "icon": "rocket",
        "description": "Product Development, Operations, Go-to-Market",
        "units": 3,
    },
    "ecommerce": {
        "name": "E-Commerce",
        "icon": "shopping_bags",
        "description": "Sourcing, Store, Fulfillment, Customer Service",
        "units": 4,
    },
    "freelance-agency": {
        "name": "Freelance / Agency",
        "icon": "briefcase",
        "description": "Client Acquisition, Project Delivery, Knowledge",
        "units": 3,
    },
    "content-creator": {
        "name": "Content Creator",
        "icon": "art",
        "description": "Content Production, Community, Monetization",
        "units": 3,
    },
    "personal-productivity": {
        "name": "Personal Productivity",
        "icon": "brain",
        "description": "Deep Work, Admin, Learning",
        "units": 3,
    },
}


def init_state() -> None:
    """Initialize session state with defaults."""
    defaults = {
        "wizard_step": 0,
        "config": {},
        "template_key": None,
        "generated_path": None,
        "view": "wizard",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_template(template_key: str) -> dict[str, Any]:
    """Load a YAML template file."""
    path = TEMPLATES_DIR / f"{template_key}.yaml"
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f)


def get_config() -> dict[str, Any]:
    """Get the current working config from session state."""
    return st.session_state.get("config", {})


def set_config(config: dict[str, Any]) -> None:
    """Update the working config in session state."""
    st.session_state["config"] = config


def get_vs() -> dict[str, Any]:
    """Shortcut to get the viable_system section."""
    return get_config().get("viable_system", {})
