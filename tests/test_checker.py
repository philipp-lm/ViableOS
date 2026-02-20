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
