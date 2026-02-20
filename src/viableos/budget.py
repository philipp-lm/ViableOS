"""Budget calculator — maps strategy + monthly_usd to per-system model allocations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SYSTEM_WEIGHT = {
    "S1": 0.65,
    "S2": 0.05,
    "S3": 0.12,
    "S3*": 0.05,
    "S4": 0.10,
    "S5": 0.03,
}

FRIENDLY_NAMES = {
    "S1": "Operations",
    "S2": "Coordinator",
    "S3": "Optimizer",
    "S3*": "Auditor",
    "S4": "Scout",
    "S5": "Policy Guardian",
}

MODEL_PRESETS: dict[str, dict[str, str]] = {
    "frugal": {
        "s1_routine": "anthropic/claude-haiku-3-5",
        "s1_complex": "anthropic/claude-haiku-3-5",
        "s2_coordination": "anthropic/claude-haiku-3-5",
        "s3_optimization": "anthropic/claude-haiku-3-5",
        "s3_star_audit": "openai/gpt-4o-mini",
        "s4_intelligence": "anthropic/claude-sonnet-4-5",
        "s5_preparation": "anthropic/claude-haiku-3-5",
    },
    "balanced": {
        "s1_routine": "anthropic/claude-haiku-3-5",
        "s1_complex": "anthropic/claude-sonnet-4-5",
        "s2_coordination": "anthropic/claude-haiku-3-5",
        "s3_optimization": "anthropic/claude-sonnet-4-5",
        "s3_star_audit": "openai/gpt-4o",
        "s4_intelligence": "anthropic/claude-opus-4-6",
        "s5_preparation": "anthropic/claude-sonnet-4-5",
    },
    "performance": {
        "s1_routine": "anthropic/claude-sonnet-4-5",
        "s1_complex": "anthropic/claude-opus-4-6",
        "s2_coordination": "anthropic/claude-sonnet-4-5",
        "s3_optimization": "anthropic/claude-opus-4-6",
        "s3_star_audit": "openai/gpt-4o",
        "s4_intelligence": "anthropic/claude-opus-4-6",
        "s5_preparation": "anthropic/claude-opus-4-6",
    },
}

PROVIDER_OVERRIDES: dict[str, dict[str, str]] = {
    "openai": {
        "anthropic/claude-haiku-3-5": "openai/gpt-4o-mini",
        "anthropic/claude-sonnet-4-5": "openai/gpt-4o",
        "anthropic/claude-opus-4-6": "openai/o3",
    },
    "ollama": {
        "anthropic/claude-haiku-3-5": "ollama/llama3.3-8b",
        "anthropic/claude-sonnet-4-5": "ollama/llama3.3-70b",
        "anthropic/claude-opus-4-6": "ollama/llama3.3-70b",
        "openai/gpt-4o": "ollama/mistral-large",
        "openai/gpt-4o-mini": "ollama/mistral-7b",
    },
}


@dataclass
class BudgetAllocation:
    system: str
    friendly_name: str
    monthly_usd: float
    model: str
    percentage: float


@dataclass
class BudgetPlan:
    total_monthly_usd: float
    strategy: str
    allocations: list[BudgetAllocation]
    model_routing: dict[str, str]


def _apply_provider_pref(model: str, provider: str) -> str:
    """Swap model to match preferred provider."""
    if provider in PROVIDER_OVERRIDES:
        return PROVIDER_OVERRIDES[provider].get(model, model)
    return model


def calculate_budget(config: dict[str, Any]) -> BudgetPlan:
    """Calculate budget allocations from a parsed ViableOS config."""
    vs = config.get("viable_system", {})
    budget_cfg = vs.get("budget", {})
    monthly = budget_cfg.get("monthly_usd", 150.0)
    strategy = budget_cfg.get("strategy", "balanced")
    provider = vs.get("model_routing", {}).get("provider_preference", "anthropic")
    explicit_routing = vs.get("model_routing", {})

    presets = MODEL_PRESETS.get(strategy, MODEL_PRESETS["balanced"])
    s1_units = vs.get("system_1", [])
    num_s1 = max(len(s1_units), 1)

    routing: dict[str, str] = {}
    for key, model in presets.items():
        explicit = explicit_routing.get(key)
        if explicit:
            routing[key] = explicit
        else:
            routing[key] = _apply_provider_pref(model, provider)

    # Cross-provider audit: if s3_star uses same base provider as s1, swap it
    s1_provider = routing["s1_routine"].split("/")[0]
    s3star_provider = routing["s3_star_audit"].split("/")[0]
    if s1_provider == s3star_provider:
        if s1_provider == "anthropic":
            routing["s3_star_audit"] = "openai/gpt-4o"
        elif s1_provider == "openai":
            routing["s3_star_audit"] = "anthropic/claude-sonnet-4-5"

    allocations: list[BudgetAllocation] = []

    s1_budget = monthly * SYSTEM_WEIGHT["S1"]
    per_unit = s1_budget / num_s1
    for unit in s1_units:
        allocations.append(
            BudgetAllocation(
                system=f"S1:{unit.get('name', '?')}",
                friendly_name=unit.get("name", "?"),
                monthly_usd=round(per_unit, 2),
                model=routing["s1_routine"],
                percentage=round(SYSTEM_WEIGHT["S1"] / num_s1 * 100, 1),
            )
        )

    for sys_key in ["S2", "S3", "S3*", "S4", "S5"]:
        routing_key = {
            "S2": "s2_coordination",
            "S3": "s3_optimization",
            "S3*": "s3_star_audit",
            "S4": "s4_intelligence",
            "S5": "s5_preparation",
        }[sys_key]
        alloc_usd = monthly * SYSTEM_WEIGHT[sys_key]
        allocations.append(
            BudgetAllocation(
                system=sys_key,
                friendly_name=FRIENDLY_NAMES[sys_key],
                monthly_usd=round(alloc_usd, 2),
                model=routing[routing_key],
                percentage=round(SYSTEM_WEIGHT[sys_key] * 100, 1),
            )
        )

    return BudgetPlan(
        total_monthly_usd=monthly,
        strategy=strategy,
        allocations=allocations,
        model_routing=routing,
    )
