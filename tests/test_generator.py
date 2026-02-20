"""Tests for the OpenClaw package generator."""

import json
from pathlib import Path

from viableos.generator import generate_openclaw_package
from viableos.schema import validate


def _full_config() -> dict:
    return {
        "viable_system": {
            "name": "Test SaaS",
            "runtime": "openclaw",
            "identity": {
                "purpose": "Build great software",
                "values": ["Ship fast", "User first"],
                "never_do": ["Delete production data", "Send emails without approval"],
                "decisions_requiring_human": ["deployments"],
            },
            "budget": {"monthly_usd": 200, "strategy": "balanced"},
            "model_routing": {"provider_preference": "anthropic"},
            "human_in_the_loop": {
                "notification_channel": "whatsapp",
                "approval_required": ["deployments"],
                "review_required": ["features"],
                "emergency_alerts": ["data_leak"],
            },
            "system_1": [
                {"name": "Dev", "purpose": "Build software", "autonomy": "Fix bugs alone", "tools": ["github"], "model": "openai/gpt-5.1-codex", "weight": 8},
                {"name": "Sales", "purpose": "Close deals", "tools": ["crm"], "weight": 3},
            ],
            "system_2": {
                "coordination_rules": [
                    {"trigger": "Dev deploys", "action": "Notify Sales"},
                ]
            },
            "system_3": {
                "reporting_rhythm": "weekly",
                "resource_allocation": "Dev 70%, Sales 30%",
            },
            "system_3_star": {
                "schedule": "bi-weekly",
                "checks": [
                    {"name": "Quality", "target": "Dev", "method": "Review commits"},
                ],
                "on_failure": "Alert human",
            },
            "system_4": {
                "monitoring": {
                    "competitors": ["Rival"],
                    "technology": ["AI models"],
                    "regulation": ["GDPR"],
                }
            },
        }
    }


def test_config_validates():
    errors = validate(_full_config())
    assert errors == []


def test_generates_output_directory(tmp_path: Path):
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    assert out.exists()
    assert (out / "openclaw.json").exists()
    assert (out / "install.sh").exists()


def test_generates_all_agents(tmp_path: Path):
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    workspaces = list((out / "workspaces").iterdir())
    expected = {"s1-dev", "s1-sales", "s2-coordination", "s3-optimization", "s3star-audit", "s4-intelligence", "s5-policy"}
    assert {w.name for w in workspaces} == expected


def test_each_agent_has_soul_and_agents_md(tmp_path: Path):
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    for ws in (out / "workspaces").iterdir():
        assert (ws / "SOUL.md").exists(), f"Missing SOUL.md in {ws.name}"
        assert (ws / "AGENTS.md").exists(), f"Missing AGENTS.md in {ws.name}"


def test_soul_contains_agent_info(tmp_path: Path):
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    dev_soul = (out / "workspaces" / "s1-dev" / "SOUL.md").read_text()
    assert "Dev" in dev_soul
    assert "Build software" in dev_soul
    assert "github" in dev_soul


def test_openclaw_json_structure(tmp_path: Path):
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    data = json.loads((out / "openclaw.json").read_text())
    assert "agents" in data
    assert "bindings" in data
    agents = data["agents"]["list"]
    assert len(agents) == 7


def test_shared_org_memory(tmp_path: Path):
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    mem = (out / "shared" / "org_memory.md").read_text()
    assert "Test SaaS" in mem
    assert "Dev" in mem


def test_install_script_executable(tmp_path: Path):
    import os
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    script = out / "install.sh"
    assert os.access(script, os.X_OK)


def test_auditor_uses_different_provider_than_routing_default(tmp_path: Path):
    """Auditor cross-provider is enforced at routing level (s1_routine vs s3_star_audit)."""
    from viableos.budget import calculate_budget
    plan = calculate_budget(_full_config())
    s1_default_prov = plan.model_routing["s1_routine"].split("/")[0]
    audit_prov = plan.model_routing["s3_star_audit"].split("/")[0]
    assert s1_default_prov != audit_prov


def test_overwrites_existing_output(tmp_path: Path):
    out_dir = tmp_path / "pkg"
    generate_openclaw_package(_full_config(), out_dir)
    out = generate_openclaw_package(_full_config(), out_dir)
    assert out.exists()
    assert (out / "openclaw.json").exists()


def test_per_unit_model_in_openclaw_json(tmp_path: Path):
    """Dev has explicit model override — should appear in openclaw.json."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    data = json.loads((out / "openclaw.json").read_text())
    agents = {a["id"]: a for a in data["agents"]["list"]}
    assert agents["s1-dev"]["model"] == "openai/gpt-5.1-codex"


def test_per_unit_weight_affects_budget(tmp_path: Path):
    """Dev (weight 8) should get more budget than Sales (weight 3)."""
    from viableos.budget import calculate_budget
    plan = calculate_budget(_full_config())
    dev_alloc = next(a for a in plan.allocations if a.system == "S1:Dev")
    sales_alloc = next(a for a in plan.allocations if a.system == "S1:Sales")
    assert dev_alloc.monthly_usd > sales_alloc.monthly_usd


def test_each_agent_has_skill_md(tmp_path: Path):
    """Every agent workspace should have a SKILL.md."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    for ws in (out / "workspaces").iterdir():
        assert (ws / "SKILL.md").exists(), f"Missing SKILL.md in {ws.name}"


def test_s1_skill_has_anti_looping(tmp_path: Path):
    """S1 SKILL.md should contain anti-looping protocol."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    skill = (out / "workspaces" / "s1-dev" / "SKILL.md").read_text()
    assert "anti-loop" in skill.lower() or "loop" in skill.lower()


def test_s1_soul_has_identity_refresh(tmp_path: Path):
    """S1 SOUL.md should contain identity refresh section (anti-echoing)."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    soul = (out / "workspaces" / "s1-dev" / "SOUL.md").read_text()
    assert "identity refresh" in soul.lower()


def test_auto_generates_coordination_rules(tmp_path: Path):
    """Even with manual rules, auto-generated rules should be merged."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    coord_soul = (out / "workspaces" / "s2-coordination" / "SOUL.md").read_text()
    assert "loop" in coord_soul.lower() or "repeat" in coord_soul.lower()


def test_coordination_rules_file_generated(tmp_path: Path):
    """shared/coordination_rules.md should be generated."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    rules_file = out / "shared" / "coordination_rules.md"
    assert rules_file.exists()
    content = rules_file.read_text()
    assert "loop" in content.lower() or "repeat" in content.lower()


def test_tool_scoping_in_openclaw_json(tmp_path: Path):
    """S1 units with tools should have tools.allow in openclaw.json."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    data = json.loads((out / "openclaw.json").read_text())
    agents = {a["id"]: a for a in data["agents"]["list"]}
    dev = agents["s1-dev"]
    assert "tools" in dev
    assert "github" in dev["tools"]["allow"]


def test_heartbeat_md_generated(tmp_path: Path):
    """Every agent workspace should have a HEARTBEAT.md."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    for ws in (out / "workspaces").iterdir():
        assert (ws / "HEARTBEAT.md").exists(), f"Missing HEARTBEAT.md in {ws.name}"


def test_user_md_generated(tmp_path: Path):
    """Every agent workspace should have a USER.md."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    for ws in (out / "workspaces").iterdir():
        assert (ws / "USER.md").exists(), f"Missing USER.md in {ws.name}"
    user_md = (out / "workspaces" / "s1-dev" / "USER.md").read_text()
    assert "Test SaaS" in user_md
    assert "whatsapp" in user_md


def test_memory_md_generated(tmp_path: Path):
    """Every agent workspace should have a MEMORY.md."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    for ws in (out / "workspaces").iterdir():
        assert (ws / "MEMORY.md").exists(), f"Missing MEMORY.md in {ws.name}"


def test_openclaw_json_has_agent_to_agent(tmp_path: Path):
    """openclaw.json should have agentToAgent communication matrix."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    data = json.loads((out / "openclaw.json").read_text())
    assert "agentToAgent" in data
    assert data["agentToAgent"]["enabled"] is True
    allow = data["agentToAgent"]["allow"]
    assert "s2-coordination" in allow
    assert "s1-dev" in allow
    assert allow["s1-dev"] == ["s2-coordination"]


def test_openclaw_json_has_fallbacks(tmp_path: Path):
    """Agents should have fallback chains in openclaw.json."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    data = json.loads((out / "openclaw.json").read_text())
    agents = {a["id"]: a for a in data["agents"]["list"]}
    dev = agents["s1-dev"]
    assert "fallbacks" in dev
    assert len(dev["fallbacks"]) >= 1


def test_openclaw_json_has_heartbeat_model(tmp_path: Path):
    """Agents should have heartbeat_model (cheaper than primary) in openclaw.json."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    data = json.loads((out / "openclaw.json").read_text())
    agents_with_hb = [a for a in data["agents"]["list"] if "heartbeat_model" in a]
    assert len(agents_with_hb) >= 1


def test_install_sh_has_prereq_check(tmp_path: Path):
    """install.sh should check for openclaw installation."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    script = (out / "install.sh").read_text()
    assert "command -v openclaw" in script


def test_install_sh_has_phased_rollout(tmp_path: Path):
    """install.sh should have phased rollout (Phase 1, 2, 3)."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    script = (out / "install.sh").read_text()
    assert "Phase 1" in script
    assert "Phase 3" in script
    assert "Start Small" in script


def test_s2_skill_has_coordination_protocol(tmp_path: Path):
    """S2 SKILL.md should contain coordination protocol."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    skill = (out / "workspaces" / "s2-coordination" / "SKILL.md").read_text()
    assert "coordination protocol" in skill.lower()
    assert "Dev" in skill
    assert "Sales" in skill


def test_s3star_skill_has_audit_protocol(tmp_path: Path):
    """S3* SKILL.md should contain audit protocol."""
    out = generate_openclaw_package(_full_config(), tmp_path / "pkg")
    skill = (out / "workspaces" / "s3star-audit" / "SKILL.md").read_text()
    assert "audit protocol" in skill.lower()
    assert "READ-ONLY" in skill
