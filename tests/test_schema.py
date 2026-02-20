"""Tests for the YAML schema validation."""

from pathlib import Path

from viableos.schema import load_yaml, validate

FIXTURES = Path(__file__).parent / "fixtures"


class TestValidate:
    def test_complete_config_is_valid(self):
        config = load_yaml(FIXTURES / "complete.yaml")
        assert validate(config) == []

    def test_minimal_config_is_valid(self):
        config = load_yaml(FIXTURES / "minimal.yaml")
        assert validate(config) == []

    def test_invalid_config_has_errors(self):
        config = load_yaml(FIXTURES / "invalid.yaml")
        errors = validate(config)
        assert len(errors) > 0

    def test_missing_viable_system_key(self):
        errors = validate({"something_else": {}})
        assert any("viable_system" in e for e in errors)

    def test_missing_required_name(self):
        config = {
            "viable_system": {
                "identity": {"purpose": "test"},
                "system_1": [{"name": "u", "purpose": "p"}],
            }
        }
        errors = validate(config)
        assert any("name" in e for e in errors)

    def test_missing_required_identity(self):
        config = {
            "viable_system": {
                "name": "Test",
                "system_1": [{"name": "u", "purpose": "p"}],
            }
        }
        errors = validate(config)
        assert any("identity" in e for e in errors)

    def test_missing_required_system_1(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "test"},
            }
        }
        errors = validate(config)
        assert any("system_1" in e for e in errors)

    def test_empty_system_1_rejected(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "test"},
                "system_1": [],
            }
        }
        errors = validate(config)
        assert len(errors) > 0

    def test_healthcare_example_is_valid(self):
        config = load_yaml(FIXTURES / ".." / ".." / "examples" / "healthcare-saas.yaml")
        assert validate(config) == []

    def test_additional_properties_rejected(self):
        config = {
            "viable_system": {
                "name": "Test",
                "identity": {"purpose": "test"},
                "system_1": [{"name": "u", "purpose": "p"}],
                "unknown_field": "bad",
            }
        }
        errors = validate(config)
        assert len(errors) > 0
