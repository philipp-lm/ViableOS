"""Tests for the budget calculator."""

from viableos.budget import BudgetPlan, calculate_budget


def _make_config(
    monthly_usd: float = 150.0,
    strategy: str = "balanced",
    provider: str = "anthropic",
    num_units: int = 3,
) -> dict:
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
    assert "opus" in plan.model_routing["s1_complex"] or "o3" in plan.model_routing["s1_complex"]


def test_openai_provider_swaps_models():
    plan = calculate_budget(_make_config(provider="openai"))
    assert "openai" in plan.model_routing["s1_routine"]


def test_cross_provider_audit():
    plan_anthropic = calculate_budget(_make_config(provider="anthropic"))
    s1_prov = plan_anthropic.model_routing["s1_routine"].split("/")[0]
    audit_prov = plan_anthropic.model_routing["s3_star_audit"].split("/")[0]
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
