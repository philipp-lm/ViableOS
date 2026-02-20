"""Auto-generate S2 coordination rules from S1 units.

Addresses community painpoints: anti-looping, workspace isolation, filesystem
boundaries, structured communication, and echoing prevention.
"""

from __future__ import annotations

from typing import Any


def generate_base_rules(s1_units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate baseline coordination rules from S1 unit configuration.

    These rules encode the hard-won lessons from the multi-agent community:
    - Anti-looping (agents repeating outputs)
    - Workspace isolation (prevents cross-contamination)
    - Filesystem boundaries (agents stay in their directory)
    - Structured communication (prevents echoing/role loss)
    - Session length limits (prevents context degradation)
    """
    rules: list[dict[str, Any]] = []
    unit_names = [u.get("name", f"Unit {i+1}") for i, u in enumerate(s1_units)]

    rules.append({
        "trigger": "Any agent repeats the same output or action 3+ times",
        "action": "Stop execution, log the loop, and escalate to Coordinator",
    })

    rules.append({
        "trigger": "Agent attempts to create files outside its workspace directory",
        "action": "Block the action and log a filesystem violation",
    })

    rules.append({
        "trigger": "Agent-to-agent communication needed",
        "action": "Route through Coordinator using structured JSON — no direct free-text conversation between agents",
    })

    rules.append({
        "trigger": "Agent conversation exceeds 7 turns without resolution",
        "action": "Summarize context, refresh identity from SOUL.md, start new session",
    })

    rules.append({
        "trigger": "Agent session history exceeds 10k tokens",
        "action": "Summarize and compact history — do not let context grow unbounded",
    })

    for name in unit_names:
        rules.append({
            "trigger": f"{name} needs to access another unit's workspace or data",
            "action": "Request via Coordinator — direct cross-workspace access is forbidden",
        })

    if len(s1_units) >= 2:
        for i, unit in enumerate(s1_units):
            for j, other in enumerate(s1_units):
                if i < j:
                    n1 = unit.get("name", f"Unit {i+1}")
                    n2 = other.get("name", f"Unit {j+1}")
                    rules.append({
                        "trigger": f"{n1} makes changes that affect {n2}'s domain",
                        "action": f"Coordinator notifies {n2} before changes are applied",
                    })

    return rules


def merge_rules(
    auto_rules: list[dict[str, Any]],
    manual_rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge auto-generated rules with manually defined rules.

    Manual rules take precedence — if a manual rule covers the same trigger
    pattern, the auto-generated version is dropped.
    """
    manual_triggers = {r.get("trigger", "").lower() for r in manual_rules}

    merged = list(manual_rules)
    for rule in auto_rules:
        trigger_lower = rule.get("trigger", "").lower()
        already_covered = any(
            trigger_lower in mt or mt in trigger_lower
            for mt in manual_triggers
            if mt
        )
        if not already_covered:
            merged.append(rule)

    return merged


def generate_workspace_isolation_rules(s1_units: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Generate explicit workspace isolation directives for the generator."""
    directives = []
    for i, unit in enumerate(s1_units):
        name = unit.get("name", f"Unit {i+1}")
        slug = name.lower().replace(" ", "-").replace("&", "and")
        directives.append({
            "agent": name,
            "workspace": f"workspaces/s1-{slug}",
            "rule": f"{name} operates ONLY in workspaces/s1-{slug} — no access to other agent directories",
        })
    return directives


def generate_agent_communication_matrix(s1_agent_ids: list[str]) -> dict[str, Any]:
    """Generate the VSM communication permission matrix for openclaw.json.

    VSM principle: S1 talks ONLY to S2. S2 routes to everyone. S3* has read-only on S1.
    This solves the "blind trust" security problem.
    """
    s1_pattern = "s1-*"
    allow: dict[str, list[str]] = {
        "s2-coordination": [s1_pattern, "s3-optimization", "s3star-audit", "s4-intelligence", "s5-policy"],
        "s3-optimization": [s1_pattern, "s2-coordination"],
        "s3star-audit": [s1_pattern],
        "s4-intelligence": ["s2-coordination", "s5-policy"],
        "s5-policy": ["s2-coordination", "s3-optimization", "s4-intelligence"],
    }

    for agent_id in s1_agent_ids:
        allow[agent_id] = ["s2-coordination"]

    return {
        "agentToAgent": {
            "enabled": True,
            "allow": allow,
        },
        "subagents": {
            "allowAgents": ["s2-coordination", "s3-optimization"],
        },
    }
