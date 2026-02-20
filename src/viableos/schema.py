"""JSON Schema definition for ViableOS YAML configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jsonschema
import yaml

VIABLEOS_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["viable_system"],
    "additionalProperties": False,
    "properties": {
        "viable_system": {
            "type": "object",
            "required": ["name", "identity", "system_1"],
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "runtime": {
                    "type": "string",
                    "enum": [
                        "openclaw",
                        "langgraph",
                        "crewai",
                        "openai-agents",
                        "cursor",
                    ],
                },
                "identity": {
                    "type": "object",
                    "required": ["purpose"],
                    "additionalProperties": False,
                    "properties": {
                        "purpose": {"type": "string"},
                        "values": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "decisions_requiring_human": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                "system_1": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "purpose"],
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "purpose": {"type": "string", "minLength": 1},
                            "autonomy": {"type": "string"},
                            "tools": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "system_2": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "coordination_rules": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["trigger", "action"],
                                "additionalProperties": False,
                                "properties": {
                                    "trigger": {
                                        "type": "string",
                                        "minLength": 1,
                                    },
                                    "action": {
                                        "type": "string",
                                        "minLength": 1,
                                    },
                                },
                            },
                        },
                    },
                },
                "system_3": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "reporting_rhythm": {"type": "string"},
                        "resource_allocation": {"type": "string"},
                    },
                },
                "system_3_star": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "schedule": {"type": "string"},
                        "checks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["name", "target", "method"],
                                "additionalProperties": False,
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "minLength": 1,
                                    },
                                    "target": {
                                        "type": "string",
                                        "minLength": 1,
                                    },
                                    "method": {
                                        "type": "string",
                                        "minLength": 1,
                                    },
                                },
                            },
                        },
                        "on_failure": {"type": "string"},
                    },
                },
                "system_4": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "monitoring": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "competitors": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "technology": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "regulation": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load and parse a YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def validate(config: dict[str, Any]) -> list[str]:
    """Validate a config dict against the ViableOS schema.

    Returns a list of validation error messages (empty if valid).
    """
    validator = jsonschema.Draft202012Validator(VIABLEOS_SCHEMA)
    return [e.message for e in sorted(validator.iter_errors(config), key=str)]
