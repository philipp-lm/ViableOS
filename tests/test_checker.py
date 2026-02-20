"""Tests for the VSM Completeness Checker."""

from pathlib import Path

from viableos.checker import check_viability
from viableos.schema import load_yaml

FIXTURES = Path(__file__).parent / "fixtures"


class TestCheckViability:
    def test_complete_config_scores_6(self):
        config = load_yaml(FIXTURES / "complete.yaml")
        report = check_viability(config)
        assert report.score == 6
        assert report.total == 6
        assert all(c.present for c in report.checks)

    def test_minimal_config_scores_2(self):
        """Minimal has only S1 and S5 (identity with purpose)."""
        config = load_yaml(FIXTURES / "minimal.yaml")
        report = check_viability(config)
        assert report.score == 2
        assert report.total == 6

        present = {c.system for c in report.checks if c.present}
        assert present == {"S1", "S5"}

    def test_missing_systems_have_suggestions(self):
        config = load_yaml(FIXTURES / "minimal.yaml")
        report = check_viability(config)
        for c in report.checks:
            if not c.present:
                assert len(c.suggestions) > 0

    def test_empty_purpose_is_not_present(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": ""},
                "system_1": [{"name": "u", "purpose": "p"}],
            }
        }
        report = check_viability(config)
        s5 = next(c for c in report.checks if c.system == "S5")
        assert not s5.present

    def test_whitespace_only_purpose_is_not_present(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "   "},
                "system_1": [{"name": "u", "purpose": "p"}],
            }
        }
        report = check_viability(config)
        s5 = next(c for c in report.checks if c.system == "S5")
        assert not s5.present

    def test_s1_details_lists_unit_names(self):
        config = load_yaml(FIXTURES / "complete.yaml")
        report = check_viability(config)
        s1 = next(c for c in report.checks if c.system == "S1")
        assert "Unit A" in s1.details
        assert "Unit B" in s1.details

    def test_s2_counts_rules(self):
        config = load_yaml(FIXTURES / "complete.yaml")
        report = check_viability(config)
        s2 = next(c for c in report.checks if c.system == "S2")
        assert "1 rule" in s2.details

    def test_s3_star_lists_check_names(self):
        config = load_yaml(FIXTURES / "complete.yaml")
        report = check_viability(config)
        s3star = next(c for c in report.checks if c.system == "S3*")
        assert "Quality Check" in s3star.details

    def test_healthcare_example_scores_6(self):
        config = load_yaml(FIXTURES / ".." / ".." / "examples" / "healthcare-saas.yaml")
        report = check_viability(config)
        assert report.score == 6

    def test_empty_config(self):
        config = {"viable_system": {}}
        report = check_viability(config)
        assert report.score == 0
        assert report.total == 6


class TestCommunityWarnings:
    """Tests for community-driven warnings (painpoints 1-7)."""

    def test_no_budget_gives_critical_warning(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [{"name": "u", "purpose": "p"}],
            }
        }
        report = check_viability(config)
        budget_warnings = [w for w in report.warnings if w.category == "Token Budget"]
        assert any(w.severity == "critical" for w in budget_warnings)

    def test_budget_without_alerts_gives_warning(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [{"name": "u", "purpose": "p"}],
                "budget": {"monthly_usd": 100},
            }
        }
        report = check_viability(config)
        budget_warnings = [w for w in report.warnings if w.category == "Token Budget"]
        assert any(w.severity == "warning" for w in budget_warnings)

    def test_model_warning_for_known_bad_model(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [{"name": "u", "purpose": "p", "model": "deepseek/deepseek-v3.2"}],
            }
        }
        report = check_viability(config)
        model_warnings = [w for w in report.warnings if w.category == "Model Warning"]
        assert len(model_warnings) >= 1
        assert "deepseek" in model_warnings[0].message.lower()

    def test_no_persistence_gives_warning(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [{"name": "u", "purpose": "p"}],
            }
        }
        report = check_viability(config)
        persistence_warnings = [w for w in report.warnings if w.category == "Persistence"]
        assert len(persistence_warnings) >= 1

    def test_persistence_sqlite_no_warning(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [{"name": "u", "purpose": "p"}],
                "persistence": {"strategy": "sqlite", "path": "./state"},
            }
        }
        report = check_viability(config)
        persistence_warnings = [w for w in report.warnings if w.category == "Persistence"]
        assert len(persistence_warnings) == 0

    def test_sensitive_tools_without_audit_critical(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [{"name": "u", "purpose": "p", "tools": ["ssh", "deployment"]}],
            }
        }
        report = check_viability(config)
        security_warnings = [w for w in report.warnings if w.category == "Security"]
        assert any(w.severity == "critical" for w in security_warnings)

    def test_no_never_do_gives_info(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [{"name": "u", "purpose": "p"}],
            }
        }
        report = check_viability(config)
        security_warnings = [w for w in report.warnings if w.category == "Security"]
        assert any(w.severity == "info" and "never do" in w.message.lower() for w in security_warnings)

    def test_multiple_units_without_manual_rules_info(self):
        """2+ units without manual rules gets an info (auto-rules cover the base)."""
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [
                    {"name": "A", "purpose": "a"},
                    {"name": "B", "purpose": "b"},
                ],
            }
        }
        report = check_viability(config)
        coord_warnings = [w for w in report.warnings if w.category == "Coordination"]
        assert any(w.severity == "info" and "auto-generated" in w.message.lower() for w in coord_warnings)
        assert not any(w.message == "No anti-looping rule found." for w in coord_warnings)

    def test_many_units_without_hitl_warns_rollout(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "Test"},
                "system_1": [
                    {"name": "A", "purpose": "a"},
                    {"name": "B", "purpose": "b"},
                    {"name": "C", "purpose": "c"},
                    {"name": "D", "purpose": "d"},
                ],
            }
        }
        report = check_viability(config)
        rollout_warnings = [w for w in report.warnings if w.category == "Rollout"]
        assert any("start with 1-2" in w.message.lower() for w in rollout_warnings)
