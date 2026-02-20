"""Budget calculator — maps strategy + monthly_usd to per-system model allocations.

Supports per-unit model and weight overrides from the config.
"""

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

# ── Full model catalog (Feb 2026) ───────────────────────────────────────────

MODEL_CATALOG: dict[str, dict[str, str]] = {
    # Anthropic
    "anthropic/claude-opus-4-6": {"provider": "anthropic", "tier": "premium", "note": "Best reasoning + agents"},
    "anthropic/claude-sonnet-4-6": {"provider": "anthropic", "tier": "high", "note": "Best speed/quality balance"},
    "anthropic/claude-haiku-4-5": {"provider": "anthropic", "tier": "fast", "note": "Fast, cheap, near-frontier"},
    "anthropic/claude-opus-4-5": {"provider": "anthropic", "tier": "premium", "note": "Previous gen top"},
    "anthropic/claude-sonnet-4-5": {"provider": "anthropic", "tier": "high", "note": "Previous gen high"},
    # OpenAI
    "openai/gpt-5.3-codex": {"provider": "openai", "tier": "premium", "note": "Best agentic coding model (Feb 2026)"},
    "openai/gpt-5.3-codex-spark": {"provider": "openai", "tier": "high", "note": "Ultra-fast coding, 1000+ tok/s"},
    "openai/gpt-5.2": {"provider": "openai", "tier": "premium", "note": "Latest flagship"},
    "openai/gpt-5.1": {"provider": "openai", "tier": "high", "note": "Strong all-round"},
    "openai/gpt-5.1-codex": {"provider": "openai", "tier": "premium", "note": "Code-focused"},
    "openai/gpt-5-mini": {"provider": "openai", "tier": "fast", "note": "Budget flagship"},
    "openai/gpt-5-codex-mini": {"provider": "openai", "tier": "fast", "note": "Budget code model"},
    "openai/o3": {"provider": "openai", "tier": "premium", "note": "Specialized reasoning"},
    # Google
    "google/gemini-3-pro": {"provider": "google", "tier": "premium", "note": "Top-ranked overall"},
    "google/gemini-3-flash": {"provider": "google", "tier": "high", "note": "Fast + capable"},
    "google/gemini-2.5-pro": {"provider": "google", "tier": "high", "note": "Strong reasoning"},
    "google/gemini-2.5-flash": {"provider": "google", "tier": "fast", "note": "Budget, 1M context"},
    "google/gemini-2.5-flash-lite": {"provider": "google", "tier": "budget", "note": "Cheapest Gemini"},
    # DeepSeek
    "deepseek/deepseek-v3.2": {"provider": "deepseek", "tier": "high", "note": "Open source, competitive"},
    # xAI
    "xai/grok-4": {"provider": "xai", "tier": "premium", "note": "256K context, fast"},
    # Meta
    "meta/llama-4": {"provider": "meta", "tier": "high", "note": "Open source, self-hostable"},
    # Ollama (local)
    "ollama/llama-4": {"provider": "ollama", "tier": "high", "note": "Local Llama 4"},
    "ollama/mistral-large": {"provider": "ollama", "tier": "high", "note": "Local Mistral"},
    "ollama/deepseek-v3": {"provider": "ollama", "tier": "high", "note": "Local DeepSeek"},
}

MODEL_TIERS = {
    "premium": "Premium — best quality, highest cost",
    "high": "High — strong quality, moderate cost",
    "fast": "Fast — good quality, low cost",
    "budget": "Budget — basic quality, minimal cost",
}

# ── Strategy presets (updated to Feb 2026 models) ───────────────────────────

MODEL_PRESETS: dict[str, dict[str, str]] = {
    "frugal": {
        "s1_routine": "anthropic/claude-haiku-4-5",
        "s1_complex": "anthropic/claude-haiku-4-5",
        "s2_coordination": "anthropic/claude-haiku-4-5",
        "s3_optimization": "anthropic/claude-haiku-4-5",
        "s3_star_audit": "openai/gpt-5-mini",
        "s4_intelligence": "anthropic/claude-sonnet-4-6",
        "s5_preparation": "anthropic/claude-haiku-4-5",
    },
    "balanced": {
        "s1_routine": "anthropic/claude-haiku-4-5",
        "s1_complex": "anthropic/claude-sonnet-4-6",
        "s2_coordination": "anthropic/claude-haiku-4-5",
        "s3_optimization": "anthropic/claude-sonnet-4-6",
        "s3_star_audit": "openai/gpt-5.1",
        "s4_intelligence": "anthropic/claude-opus-4-6",
        "s5_preparation": "anthropic/claude-sonnet-4-6",
    },
    "performance": {
        "s1_routine": "anthropic/claude-sonnet-4-6",
        "s1_complex": "anthropic/claude-opus-4-6",
        "s2_coordination": "anthropic/claude-sonnet-4-6",
        "s3_optimization": "anthropic/claude-opus-4-6",
        "s3_star_audit": "openai/gpt-5.2",
        "s4_intelligence": "google/gemini-3-pro",
        "s5_preparation": "anthropic/claude-opus-4-6",
    },
}

PROVIDER_OVERRIDES: dict[str, dict[str, str]] = {
    "openai": {
        "anthropic/claude-haiku-4-5": "openai/gpt-5-mini",
        "anthropic/claude-sonnet-4-6": "openai/gpt-5.1",
        "anthropic/claude-opus-4-6": "openai/gpt-5.2",
    },
    "google": {
        "anthropic/claude-haiku-4-5": "google/gemini-2.5-flash",
        "anthropic/claude-sonnet-4-6": "google/gemini-3-flash",
        "anthropic/claude-opus-4-6": "google/gemini-3-pro",
        "openai/gpt-5-mini": "google/gemini-2.5-flash",
        "openai/gpt-5.1": "google/gemini-3-flash",
        "openai/gpt-5.2": "google/gemini-3-pro",
    },
    "deepseek": {
        "anthropic/claude-haiku-4-5": "deepseek/deepseek-v3.2",
        "anthropic/claude-sonnet-4-6": "deepseek/deepseek-v3.2",
        "anthropic/claude-opus-4-6": "deepseek/deepseek-v3.2",
    },
    "xai": {
        "anthropic/claude-haiku-4-5": "xai/grok-4",
        "anthropic/claude-sonnet-4-6": "xai/grok-4",
        "anthropic/claude-opus-4-6": "xai/grok-4",
    },
    "meta": {
        "anthropic/claude-haiku-4-5": "meta/llama-4",
        "anthropic/claude-sonnet-4-6": "meta/llama-4",
        "anthropic/claude-opus-4-6": "meta/llama-4",
    },
    "ollama": {
        "anthropic/claude-haiku-4-5": "ollama/llama-4",
        "anthropic/claude-sonnet-4-6": "ollama/llama-4",
        "anthropic/claude-opus-4-6": "ollama/llama-4",
        "openai/gpt-5-mini": "ollama/llama-4",
        "openai/gpt-5.1": "ollama/mistral-large",
        "openai/gpt-5.2": "ollama/deepseek-v3",
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


def get_models_for_provider(provider: str) -> list[str]:
    """Return model IDs available for a given provider."""
    if provider == "mixed":
        return sorted(MODEL_CATALOG.keys())
    return sorted(
        m for m, info in MODEL_CATALOG.items()
        if info["provider"] == provider
    )


def get_all_models() -> list[str]:
    """Return all model IDs sorted by provider."""
    return sorted(MODEL_CATALOG.keys())


def calculate_budget(config: dict[str, Any]) -> BudgetPlan:
    """Calculate budget allocations from a parsed ViableOS config.

    Respects per-unit `model` and `weight` overrides in system_1 items.
    """
    vs = config.get("viable_system", {})
    budget_cfg = vs.get("budget", {})
    monthly = budget_cfg.get("monthly_usd", 150.0)
    strategy = budget_cfg.get("strategy", "balanced")
    provider = vs.get("model_routing", {}).get("provider_preference", "anthropic")
    explicit_routing = vs.get("model_routing", {})

    presets = MODEL_PRESETS.get(strategy, MODEL_PRESETS["balanced"])
    s1_units = vs.get("system_1", [])

    routing: dict[str, str] = {}
    for key, model in presets.items():
        explicit = explicit_routing.get(key)
        if explicit:
            routing[key] = explicit
        else:
            routing[key] = _apply_provider_pref(model, provider)

    # Cross-provider audit
    s1_provider = routing["s1_routine"].split("/")[0]
    s3star_provider = routing["s3_star_audit"].split("/")[0]
    if s1_provider == s3star_provider:
        if s1_provider == "anthropic":
            routing["s3_star_audit"] = "openai/gpt-5.1"
        elif s1_provider == "openai":
            routing["s3_star_audit"] = "anthropic/claude-sonnet-4-6"
        elif s1_provider == "google":
            routing["s3_star_audit"] = "anthropic/claude-sonnet-4-6"
        else:
            routing["s3_star_audit"] = "openai/gpt-5.1"

    allocations: list[BudgetAllocation] = []

    # S1 units with per-unit weight support
    s1_budget = monthly * SYSTEM_WEIGHT["S1"]
    weights = [float(u.get("weight", 5)) for u in s1_units] if s1_units else [5.0]
    total_weight = sum(weights) or 1.0

    for i, unit in enumerate(s1_units):
        w = weights[i]
        unit_budget = s1_budget * (w / total_weight)
        unit_model = unit.get("model") or routing["s1_routine"]

        allocations.append(
            BudgetAllocation(
                system=f"S1:{unit.get('name', '?')}",
                friendly_name=unit.get("name", "?"),
                monthly_usd=round(unit_budget, 2),
                model=unit_model,
                percentage=round(SYSTEM_WEIGHT["S1"] * (w / total_weight) * 100, 1),
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
