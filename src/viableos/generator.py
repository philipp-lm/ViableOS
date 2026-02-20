"""OpenClaw package generator — turns a ViableOS config into a deployable package."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from viableos.budget import calculate_budget
from viableos.soul_templates import (
    generate_agents_md,
    generate_org_memory,
    generate_s1_soul,
    generate_s2_soul,
    generate_s3_soul,
    generate_s3star_soul,
    generate_s4_soul,
    generate_s5_soul,
)


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("&", "and")


def _make_agent_entry(
    agent_id: str,
    name: str,
    workspace: str,
    model: str,
    tools_allow: list[str] | None = None,
    tools_deny: list[str] | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": agent_id,
        "name": name,
        "workspace": workspace,
        "model": model,
    }
    if tools_allow or tools_deny:
        entry["tools"] = {}
        if tools_allow:
            entry["tools"]["allow"] = tools_allow
        if tools_deny:
            entry["tools"]["deny"] = tools_deny
    return entry


def generate_openclaw_package(
    config: dict[str, Any],
    output_dir: str | Path,
) -> Path:
    """Generate a complete OpenClaw deployment package from a ViableOS config."""
    output = Path(output_dir)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    vs = config.get("viable_system", {})
    identity = vs.get("identity", {})
    hitl = vs.get("human_in_the_loop", {})
    s1_units = vs.get("system_1", [])
    coord_rules = vs.get("system_2", {}).get("coordination_rules", [])
    s3_cfg = vs.get("system_3", {})
    s3star_cfg = vs.get("system_3_star", {})
    s4_cfg = vs.get("system_4", {})
    monitoring = s4_cfg.get("monitoring", {})

    plan = calculate_budget(config)
    s1_names = [u.get("name", "?") for u in s1_units]

    # Collect all agents for AGENTS.md
    all_agents: list[dict[str, str]] = []
    openclaw_agents: list[dict[str, Any]] = []

    workspaces_dir = output / "workspaces"
    shared_dir = output / "shared"
    workspaces_dir.mkdir()
    shared_dir.mkdir()

    # --- S1 units ---
    for i, unit in enumerate(s1_units):
        name = unit.get("name", f"Unit {i+1}")
        slug = f"s1-{_slugify(name)}"
        agent_id = slug
        ws_path = workspaces_dir / slug
        ws_path.mkdir()

        other_units = [n for n in s1_names if n != name]
        soul = generate_s1_soul(unit, identity, coord_rules, hitl, other_units)
        (ws_path / "SOUL.md").write_text(soul)

        unit_model = unit.get("model")
        if unit_model:
            model = unit_model
        else:
            alloc = next(
                (a for a in plan.allocations if a.system == f"S1:{name}"), None
            )
            model = alloc.model if alloc else plan.model_routing.get("s1_routine", "")

        all_agents.append(
            {"name": name, "role": "Operations (S1)", "purpose": unit.get("purpose", "")}
        )
        openclaw_agents.append(
            _make_agent_entry(agent_id, name, f"workspaces/{slug}", model)
        )

    # --- S2 Coordinator ---
    slug = "s2-coordination"
    ws_path = workspaces_dir / slug
    ws_path.mkdir()
    soul = generate_s2_soul(coord_rules, s1_names, identity)
    (ws_path / "SOUL.md").write_text(soul)
    all_agents.append(
        {"name": "Coordinator", "role": "Coordination (S2)", "purpose": "Prevent conflicts between units"}
    )
    openclaw_agents.append(
        _make_agent_entry(
            slug,
            "Coordinator",
            f"workspaces/{slug}",
            plan.model_routing.get("s2_coordination", ""),
            tools_allow=["read", "sessions_list", "sessions_history", "sessions_send"],
        )
    )

    # --- S3 Optimizer ---
    slug = "s3-optimization"
    ws_path = workspaces_dir / slug
    ws_path.mkdir()
    soul = generate_s3_soul(
        identity,
        s1_names,
        plan.total_monthly_usd,
        s3_cfg.get("resource_allocation", ""),
        s3_cfg.get("reporting_rhythm", ""),
    )
    (ws_path / "SOUL.md").write_text(soul)
    all_agents.append(
        {"name": "Optimizer", "role": "Optimization (S3)", "purpose": "Allocate resources, weekly digest"}
    )
    openclaw_agents.append(
        _make_agent_entry(
            slug,
            "Optimizer",
            f"workspaces/{slug}",
            plan.model_routing.get("s3_optimization", ""),
            tools_allow=["read", "write", "sessions_list", "sessions_history", "sessions_send"],
        )
    )

    # --- S3* Auditor ---
    slug = "s3star-audit"
    ws_path = workspaces_dir / slug
    ws_path.mkdir()
    checks = s3star_cfg.get("checks", [])
    on_failure = s3star_cfg.get("on_failure", "Escalate to human immediately")
    soul = generate_s3star_soul(identity, checks, s1_names, on_failure)
    (ws_path / "SOUL.md").write_text(soul)
    all_agents.append(
        {"name": "Auditor", "role": "Audit (S3*)", "purpose": "Independent quality verification"}
    )
    openclaw_agents.append(
        _make_agent_entry(
            slug,
            "Auditor",
            f"workspaces/{slug}",
            plan.model_routing.get("s3_star_audit", ""),
            tools_allow=["read", "sessions_list", "sessions_history"],
            tools_deny=["write", "edit", "apply_patch"],
        )
    )

    # --- S4 Scout ---
    slug = "s4-intelligence"
    ws_path = workspaces_dir / slug
    ws_path.mkdir()
    soul = generate_s4_soul(identity, monitoring)
    (ws_path / "SOUL.md").write_text(soul)
    all_agents.append(
        {"name": "Scout", "role": "Intelligence (S4)", "purpose": "Monitor environment, strategic briefs"}
    )
    openclaw_agents.append(
        _make_agent_entry(
            slug,
            "Scout",
            f"workspaces/{slug}",
            plan.model_routing.get("s4_intelligence", ""),
        )
    )

    # --- S5 Policy Guardian ---
    slug = "s5-policy"
    ws_path = workspaces_dir / slug
    ws_path.mkdir()
    soul = generate_s5_soul(identity, hitl)
    (ws_path / "SOUL.md").write_text(soul)
    all_agents.append(
        {"name": "Policy Guardian", "role": "Identity (S5)", "purpose": "Enforce values and policies"}
    )
    openclaw_agents.append(
        _make_agent_entry(
            slug,
            "Policy Guardian",
            f"workspaces/{slug}",
            plan.model_routing.get("s5_preparation", ""),
            tools_allow=["read", "sessions_list", "sessions_history"],
        )
    )

    # --- Write AGENTS.md to every workspace ---
    agents_md = generate_agents_md(all_agents)
    for ws in workspaces_dir.iterdir():
        if ws.is_dir():
            (ws / "AGENTS.md").write_text(agents_md)

    # --- Shared org memory ---
    org_memory = generate_org_memory(config)
    (shared_dir / "org_memory.md").write_text(org_memory)

    # --- openclaw.json ---
    channel = hitl.get("notification_channel", "whatsapp")
    openclaw_config = {
        "agents": {"list": openclaw_agents},
        "bindings": [
            {"agentId": openclaw_agents[0]["id"], "match": {"channel": channel}}
        ],
    }
    (output / "openclaw.json").write_text(
        json.dumps(openclaw_config, indent=2, ensure_ascii=False) + "\n"
    )

    # --- install.sh ---
    system_name = vs.get("name", "ViableOS System")
    install_script = f"""#!/bin/bash
# ViableOS OpenClaw Setup — {system_name}
#
# Prerequisites: OpenClaw installed (npm install -g openclaw)
#
# Usage:
#   1. Copy this entire folder to your OpenClaw server
#   2. Run: bash install.sh
#   3. Restart the gateway: openclaw gateway restart

set -e

echo "Setting up ViableOS agents for: {system_name}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"""
    for agent in openclaw_agents:
        install_script += f"""echo "Adding agent: {agent['name']}..."
openclaw agents add {agent['id']} --workspace "$SCRIPT_DIR/{agent['workspace']}" --model "{agent['model']}" --non-interactive 2>/dev/null || echo "  (agent may already exist)"
"""

    install_script += f"""
echo ""
echo "Done! {len(openclaw_agents)} agents configured."
echo ""
echo "Next steps:"
echo "  1. Configure your API keys: openclaw configure"
echo "  2. Restart the gateway: openclaw gateway restart"
echo "  3. Check status: openclaw agents list"
"""
    (output / "install.sh").write_text(install_script)
    (output / "install.sh").chmod(0o755)

    return output
