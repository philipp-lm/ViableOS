"""JSON Schema definition for ViableOS YAML configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jsonschema
import yaml

_STRING_ARRAY = {"type": "array", "items": {"type": "string"}}

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
                "budget": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "monthly_usd": {"type": "number", "minimum": 0},
                        "strategy": {
                            "type": "string",
                            "enum": ["frugal", "balanced", "performance"],
                        },
                        "alerts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["at_percent", "action"],
                                "additionalProperties": False,
                                "properties": {
                                    "at_percent": {
                                        "type": "number",
                                        "minimum": 0,
                                        "maximum": 100,
                                    },
                                    "action": {"type": "string"},
                                },
                            },
                        },
                    },
                },
                "model_routing": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "default": {"type": "string"},
                        "provider_preference": {
                            "type": "string",
                            "enum": [
                                "anthropic",
                                "openai",
                                "google",
                                "deepseek",
                                "xai",
                                "meta",
                                "mixed",
                                "ollama",
                            ],
                        },
                        "s1_routine": {"type": "string"},
                        "s1_complex": {"type": "string"},
                        "s2_coordination": {"type": "string"},
                        "s3_optimization": {"type": "string"},
                        "s3_star_audit": {"type": "string"},
                        "s4_intelligence": {"type": "string"},
                        "s5_preparation": {"type": "string"},
                        "fallback": {"type": "string"},
                    },
                },
                "human_in_the_loop": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "notification_channel": {
                            "type": "string",
                            "enum": [
                                "whatsapp",
                                "telegram",
                                "email",
                                "slack",
                                "discord",
                            ],
                        },
                        "approval_required": _STRING_ARRAY,
                        "review_required": _STRING_ARRAY,
                        "emergency_alerts": _STRING_ARRAY,
                    },
                },
                "identity": {
                    "type": "object",
                    "required": ["purpose"],
                    "additionalProperties": False,
                    "properties": {
                        "purpose": {"type": "string"},
                        "values": _STRING_ARRAY,
                        "decisions_requiring_human": _STRING_ARRAY,
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
                            "tools": _STRING_ARRAY,
                            "model": {"type": "string"},
                            "weight": {"type": "number", "minimum": 1, "maximum": 10},
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
                                "competitors": _STRING_ARRAY,
                                "technology": _STRING_ARRAY,
                                "regulation": _STRING_ARRAY,
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
