"""API routes — thin wrappers around the core ViableOS modules."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from viableos.api.models import (
    BudgetAllocationResponse,
    BudgetPlanResponse,
    CheckResultResponse,
    CoordinationRule,
    ModelInfo,
    PresetsResponse,
    TemplateItem,
    ViabilityReportResponse,
    WarningResponse,
)
from viableos.budget import (
    AGENT_RELIABILITY_LABELS,
    MODEL_CATALOG,
    MODEL_PRESETS,
    MODEL_TIERS,
    MODEL_WARNINGS,
    calculate_budget,
    get_models_for_provider,
)
from viableos.checker import check_viability
from viableos.coordination import generate_base_rules
from viableos.generator import generate_openclaw_package
from viableos.schema import validate

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TEMPLATE_INFO: dict[str, dict[str, Any]] = {
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

AUTONOMY_LEVELS = {
    "full": "Fully autonomous — can act without asking",
    "report": "Can act, but must report daily",
    "approve": "Can prepare, but needs approval to execute",
    "instruct": "Only acts on explicit instructions",
    "observe": "Read-only — can observe and suggest",
}

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

NEVER_DO_PRESETS = [
    "Delete production data",
    "Send emails or messages without human approval",
    "Access customer personal information directly",
    "Make financial transactions autonomously",
    "Modify other agents' configurations or workspaces",
    "Disable audit or monitoring systems",
    "Share API keys or credentials in outputs",
    "Install packages globally on the system",
    "Bypass human-in-the-loop approval gates",
    "Access external APIs not in the approved tools list",
]

PERSISTENCE_STRATEGIES = {
    "sqlite": "SQLite — lightweight database, good for single-server setups",
    "file": "File-based — simple text/JSON files, easy to inspect and debug",
    "notion": "Notion — cloud-based, good for human-readable state",
    "custom": "Custom — bring your own persistence layer",
    "none": "None — state is lost when sessions end (not recommended for production)",
}

router = APIRouter(prefix="/api")


@router.get("/templates")
def list_templates() -> list[TemplateItem]:
    return [
        TemplateItem(key=key, **info)
        for key, info in TEMPLATE_INFO.items()
    ]


@router.get("/templates/{key}")
def get_template(key: str) -> dict[str, Any]:
    if key == "custom":
        return {"viable_system": {"name": "", "identity": {"purpose": ""}, "system_1": []}}
    path = TEMPLATES_DIR / f"{key}.yaml"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{key}' not found")
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


@router.get("/models")
def list_models() -> list[ModelInfo]:
    return [
        ModelInfo(
            id=model_id,
            provider=info["provider"],
            tier=info["tier"],
            note=info["note"],
            agent_reliability=info["agent_reliability"],
            warning=MODEL_WARNINGS.get(model_id),
        )
        for model_id, info in MODEL_CATALOG.items()
    ]


@router.get("/models/{provider}")
def list_models_by_provider(provider: str) -> list[str]:
    return get_models_for_provider(provider)


@router.get("/presets")
def get_presets() -> PresetsResponse:
    return PresetsResponse(
        values=VALUE_PRESETS,
        autonomy_levels=AUTONOMY_LEVELS,
        tool_categories=TOOL_CATEGORIES,
        approval_presets=APPROVAL_PRESETS,
        review_presets=REVIEW_PRESETS,
        emergency_presets=EMERGENCY_PRESETS,
        notification_channels=NOTIFICATION_CHANNELS,
        never_do_presets=NEVER_DO_PRESETS,
        persistence_strategies=PERSISTENCE_STRATEGIES,
        model_tiers=MODEL_TIERS,
        agent_reliability_labels=AGENT_RELIABILITY_LABELS,
        strategy_presets=list(MODEL_PRESETS.keys()),
    )


@router.post("/validate")
def validate_config(config: dict[str, Any]) -> list[str]:
    return validate(config)


@router.post("/budget")
def compute_budget(config: dict[str, Any]) -> BudgetPlanResponse:
    plan = calculate_budget(config)
    return BudgetPlanResponse(
        total_monthly_usd=plan.total_monthly_usd,
        strategy=plan.strategy,
        allocations=[
            BudgetAllocationResponse(
                system=a.system,
                friendly_name=a.friendly_name,
                monthly_usd=a.monthly_usd,
                model=a.model,
                percentage=a.percentage,
            )
            for a in plan.allocations
        ],
        model_routing=plan.model_routing,
    )


@router.post("/check")
def run_check(config: dict[str, Any]) -> ViabilityReportResponse:
    report = check_viability(config)
    return ViabilityReportResponse(
        score=report.score,
        total=report.total,
        checks=[
            CheckResultResponse(
                system=c.system,
                name=c.name,
                present=c.present,
                details=c.details,
                suggestions=c.suggestions,
            )
            for c in report.checks
        ],
        warnings=[
            WarningResponse(
                category=w.category,
                severity=w.severity,
                message=w.message,
                suggestion=w.suggestion,
            )
            for w in report.warnings
        ],
    )


@router.post("/coordination/rules")
def auto_generate_rules(units: list[dict[str, Any]]) -> list[CoordinationRule]:
    rules = generate_base_rules(units)
    return [
        CoordinationRule(
            trigger=r.get("trigger", ""),
            action=r.get("action", ""),
            scope=r.get("scope", ""),
        )
        for r in rules
    ]


@router.post("/generate")
def generate_package(config: dict[str, Any]) -> FileResponse:
    errors = validate(config)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    tmp_dir = tempfile.mkdtemp()
    out_path = generate_openclaw_package(config, Path(tmp_dir) / "viableos-openclaw")

    zip_path = shutil.make_archive(str(out_path), "zip", str(out_path))

    return FileResponse(
        path=zip_path,
        filename="viableos-openclaw.zip",
        media_type="application/zip",
    )
