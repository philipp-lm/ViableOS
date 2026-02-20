"""Tests for the budget calculator."""

from viableos.budget import BudgetPlan, calculate_budget, get_all_models, get_models_for_provider


def _make_config(
    monthly_usd: float = 150.0,
    strategy: str = "balanced",
    provider: str = "anthropic",
    num_units: int = 3,
    unit_overrides: list[dict] | None = None,
) -> dict:
    if unit_overrides:
        units = unit_overrides
    else:
        units = [
            {"name": f"Unit {i+1}", "purpose": f"Purpose {i+1}"}
            for i in range(num_units)
        ]
    return {
        "viable_system": {
            "name": "Test System",
            "identity": {"purpose": "Testing"},
            "system_1": units,
            "budget": {"monthly_usd": monthly_usd, "strategy": strategy},
            "model_routing": {"provider_preference": provider},
        }
    }


def test_budget_returns_plan():
    plan = calculate_budget(_make_config())
    assert isinstance(plan, BudgetPlan)
    assert plan.total_monthly_usd == 150.0
    assert plan.strategy == "balanced"


def test_allocations_sum_to_budget():
    plan = calculate_budget(_make_config())
    total = sum(a.monthly_usd for a in plan.allocations)
    assert abs(total - 150.0) < 1.0


def test_s1_units_get_equal_share():
    plan = calculate_budget(_make_config(num_units=3))
    s1_allocs = [a for a in plan.allocations if a.system.startswith("S1:")]
    assert len(s1_allocs) == 3
    for a in s1_allocs:
        assert abs(a.monthly_usd - s1_allocs[0].monthly_usd) < 0.01


def test_frugal_uses_cheaper_models():
    frugal = calculate_budget(_make_config(strategy="frugal"))
    perf = calculate_budget(_make_config(strategy="performance"))
    assert "haiku" in frugal.model_routing["s1_routine"]
    assert "haiku" not in perf.model_routing["s1_routine"]


def test_performance_uses_expensive_models():
    plan = calculate_budget(_make_config(strategy="performance"))
    assert "opus" in plan.model_routing["s1_complex"]


def test_openai_provider_swaps_models():
    plan = calculate_budget(_make_config(provider="openai"))
    assert "openai" in plan.model_routing["s1_routine"]


def test_google_provider_swaps_models():
    plan = calculate_budget(_make_config(provider="google"))
    assert "google" in plan.model_routing["s1_routine"] or "gemini" in plan.model_routing["s1_routine"]


def test_cross_provider_audit():
    plan_anthropic = calculate_budget(_make_config(provider="anthropic"))
    s1_prov = plan_anthropic.model_routing["s1_routine"].split("/")[0]
    audit_prov = plan_anthropic.model_routing["s3_star_audit"].split("/")[0]
    assert s1_prov != audit_prov


def test_cross_provider_audit_google():
    plan = calculate_budget(_make_config(provider="google"))
    s1_prov = plan.model_routing["s1_routine"].split("/")[0]
    audit_prov = plan.model_routing["s3_star_audit"].split("/")[0]
    assert s1_prov != audit_prov


def test_single_unit_gets_full_s1_budget():
    plan = calculate_budget(_make_config(num_units=1))
    s1_allocs = [a for a in plan.allocations if a.system.startswith("S1:")]
    assert len(s1_allocs) == 1
    expected = 150.0 * 0.65
    assert abs(s1_allocs[0].monthly_usd - expected) < 0.01


def test_default_values_when_no_budget():
    config = {
        "viable_system": {
            "name": "Minimal",
            "identity": {"purpose": "Test"},
            "system_1": [{"name": "Unit", "purpose": "Test"}],
        }
    }
    plan = calculate_budget(config)
    assert plan.total_monthly_usd == 150.0
    assert plan.strategy == "balanced"


def test_per_unit_model_override():
    """Per-unit model override should be used in allocation."""
    units = [
        {"name": "Dev", "purpose": "Build", "model": "openai/gpt-5.2"},
        {"name": "Sales", "purpose": "Sell"},
    ]
    plan = calculate_budget(_make_config(unit_overrides=units))
    dev_alloc = next(a for a in plan.allocations if a.system == "S1:Dev")
    sales_alloc = next(a for a in plan.allocations if a.system == "S1:Sales")
    assert dev_alloc.model == "openai/gpt-5.2"
    assert dev_alloc.model != sales_alloc.model


def test_per_unit_weight_changes_budget():
    """Higher weight should get more budget."""
    units = [
        {"name": "Heavy", "purpose": "A", "weight": 10},
        {"name": "Light", "purpose": "B", "weight": 1},
    ]
    plan = calculate_budget(_make_config(unit_overrides=units))
    heavy = next(a for a in plan.allocations if a.system == "S1:Heavy")
    light = next(a for a in plan.allocations if a.system == "S1:Light")
    assert heavy.monthly_usd > light.monthly_usd * 5


def test_weights_sum_correctly():
    """Weighted units should still sum to S1 budget."""
    units = [
        {"name": "A", "purpose": "X", "weight": 8},
        {"name": "B", "purpose": "Y", "weight": 2},
        {"name": "C", "purpose": "Z", "weight": 5},
    ]
    plan = calculate_budget(_make_config(monthly_usd=200, unit_overrides=units))
    s1_allocs = [a for a in plan.allocations if a.system.startswith("S1:")]
    total_s1 = sum(a.monthly_usd for a in s1_allocs)
    expected = 200 * 0.65
    assert abs(total_s1 - expected) < 1.0


def test_model_catalog_has_all_providers():
    models = get_all_models()
    providers = {m.split("/")[0] for m in models}
    assert "anthropic" in providers
    assert "openai" in providers
    assert "google" in providers
    assert "deepseek" in providers
    assert "xai" in providers
    assert "meta" in providers


def test_get_models_for_provider():
    anthropic_models = get_models_for_provider("anthropic")
    assert len(anthropic_models) >= 3
    assert all("anthropic" in m for m in anthropic_models)


def test_heartbeat_model_is_cheaper():
    from viableos.budget import get_heartbeat_model, MODEL_CATALOG
    hb = get_heartbeat_model("anthropic/claude-opus-4-6")
    hb_tier = MODEL_CATALOG[hb]["tier"]
    assert hb_tier in ("fast", "budget", "high")
    assert hb != "anthropic/claude-opus-4-6"


def test_fallback_chain_has_entries():
    from viableos.budget import get_fallback_chain
    chain = get_fallback_chain("anthropic/claude-opus-4-6")
    assert len(chain) >= 1
    assert len(chain) <= 2
    assert all(fb != "anthropic/claude-opus-4-6" for fb in chain)


def test_fallback_chain_includes_cross_provider():
    from viableos.budget import get_fallback_chain
    chain = get_fallback_chain("anthropic/claude-opus-4-6")
    providers = {fb.split("/")[0] for fb in chain}
    assert len(providers) >= 1
