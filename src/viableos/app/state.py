"""Session state management and preset data for the ViableOS wizard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import yaml

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# ── Template metadata ────────────────────────────────────────────────────────

TEMPLATE_INFO = {
    "custom": {
        "name": "Start from Scratch",
        "tagline": "Build your own organization from zero",
        "description": "Define your own units, values, and structure",
        "units": 0,
    },
    "saas-startup": {
        "name": "SaaS Startup",
        "tagline": "Build, ship, and sell software",
        "description": "Product Development, Operations, Go-to-Market",
        "units": 3,
    },
    "ecommerce": {
        "name": "E-Commerce",
        "tagline": "Source, sell, ship, support",
        "description": "Sourcing, Store, Fulfillment, Customer Service",
        "units": 4,
    },
    "freelance-agency": {
        "name": "Freelance / Agency",
        "tagline": "Find clients, deliver, grow",
        "description": "Client Acquisition, Project Delivery, Knowledge",
        "units": 3,
    },
    "content-creator": {
        "name": "Content Creator",
        "tagline": "Create, distribute, monetize",
        "description": "Content Production, Community, Monetization",
        "units": 3,
    },
    "personal-productivity": {
        "name": "Personal Productivity",
        "tagline": "Focus on what matters",
        "description": "Deep Work, Admin, Learning",
        "units": 3,
    },
    "marketing-agency": {
        "name": "Marketing Agency",
        "tagline": "Strategy, campaigns, results",
        "description": "Strategy, Creative, Performance, Client Relations",
        "units": 4,
    },
    "consulting": {
        "name": "Consulting Firm",
        "tagline": "Advise, deliver, scale",
        "description": "Business Development, Engagement Delivery, Knowledge & IP",
        "units": 3,
    },
    "law-firm": {
        "name": "Law Firm",
        "tagline": "Research, advise, represent",
        "description": "Case Management, Legal Research, Client Relations",
        "units": 3,
    },
    "accounting": {
        "name": "Accounting Firm",
        "tagline": "Count, comply, advise",
        "description": "Bookkeeping, Tax & Compliance, Advisory",
        "units": 3,
    },
    "education": {
        "name": "Online Education",
        "tagline": "Teach, support, grow",
        "description": "Course Development, Student Success, Growth",
        "units": 3,
    },
    "restaurant": {
        "name": "Restaurant / Hospitality",
        "tagline": "Cook, serve, grow",
        "description": "Kitchen, Front-of-House, Marketing & Reservations",
        "units": 3,
    },
}

# ── Value presets ────────────────────────────────────────────────────────────

VALUE_PRESETS = [
    "Ship fast, fix fast",
    "User experience above technical elegance",
    "Customer satisfaction above everything",
    "Quality over quantity",
    "Transparency and honesty",
    "Security and privacy first",
    "Data-driven decisions",
    "Sustainability and long-term thinking",
    "Innovation over tradition",
    "Consistency builds trust",
    "Speed over perfection",
    "Reliability over features",
]

# ── Autonomy presets ─────────────────────────────────────────────────────────

AUTONOMY_LEVELS = {
    "full": "Fully autonomous — can act without asking",
    "report": "Can act, but must report daily",
    "approve": "Can prepare, but needs approval to execute",
    "instruct": "Only acts on explicit instructions",
    "observe": "Read-only — can observe and suggest",
}

# ── Tool presets by category ─────────────────────────────────────────────────

TOOL_CATEGORIES = {
    "Development": ["github", "testing", "code-review", "ci-cd", "debugging"],
    "Communication": ["email", "chat", "slack", "whatsapp", "video-calls"],
    "Content": ["writing", "editing", "research", "image-generation", "video-editing"],
    "Analytics": ["seo-analysis", "web-analytics", "reporting", "data-analysis"],
    "Commerce": ["shopify-api", "payment-processing", "inventory", "pricing-tools"],
    "Operations": ["ssh", "docker", "monitoring", "log-analysis", "deployment"],
    "Marketing": ["social-media", "ad-management", "copywriting", "email-campaigns"],
    "CRM": ["crm", "lead-tracking", "outreach", "proposal-writing"],
}

# ── HiTL presets ─────────────────────────────────────────────────────────────

APPROVAL_PRESETS = [
    "Deployments to production",
    "Publishing content",
    "Customer data access",
    "Pricing changes",
    "Sending communications on my behalf",
    "New supplier or partner deals",
    "Financial transactions",
    "Code changes to core systems",
    "Hiring or team changes",
]

REVIEW_PRESETS = [
    "Feature implementations",
    "Content drafts",
    "Marketing campaigns",
    "Financial reports",
    "Customer responses",
    "Strategic recommendations",
    "Weekly summaries",
]

EMERGENCY_PRESETS = [
    "Data leak detected",
    "Security vulnerability",
    "Budget exceeded 95%",
    "System downtime",
    "Negative viral content",
    "Legal compliance issue",
    "Customer escalation",
]

NOTIFICATION_CHANNELS = ["whatsapp", "telegram", "email", "slack", "discord"]


# ── Session state management ─────────────────────────────────────────────────

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
