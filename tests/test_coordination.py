"""Tests for the auto-generated S2 coordination rules."""

from viableos.coordination import generate_base_rules, merge_rules, generate_workspace_isolation_rules, generate_agent_communication_matrix


class TestGenerateBaseRules:
    def test_single_unit_gets_core_rules(self):
        units = [{"name": "Dev", "purpose": "Build software"}]
        rules = generate_base_rules(units)
        triggers = [r["trigger"] for r in rules]
        assert any("loop" in t.lower() or "repeat" in t.lower() for t in triggers)
        assert any("outside" in t.lower() or "filesystem" in t.lower() for t in triggers)
        assert any("communication" in t.lower() for t in triggers)
        assert any("7 turns" in t for t in triggers)
        assert any("10k tokens" in t for t in triggers)

    def test_workspace_isolation_per_unit(self):
        units = [
            {"name": "Dev", "purpose": "Build"},
            {"name": "Sales", "purpose": "Sell"},
        ]
        rules = generate_base_rules(units)
        triggers = [r["trigger"] for r in rules]
        assert any("Dev" in t and "workspace" in t.lower() for t in triggers)
        assert any("Sales" in t and "workspace" in t.lower() for t in triggers)

    def test_cross_unit_rules_for_multiple_units(self):
        units = [
            {"name": "Dev", "purpose": "Build"},
            {"name": "Sales", "purpose": "Sell"},
        ]
        rules = generate_base_rules(units)
        triggers = [r["trigger"] for r in rules]
        assert any("Dev" in t and "Sales" in t for t in triggers)

    def test_no_cross_unit_rules_for_single_unit(self):
        units = [{"name": "Dev", "purpose": "Build"}]
        rules = generate_base_rules(units)
        assert not any(
            r["trigger"].count("Dev") > 1 for r in rules
        )

    def test_three_units_get_three_cross_rules(self):
        units = [
            {"name": "A", "purpose": "a"},
            {"name": "B", "purpose": "b"},
            {"name": "C", "purpose": "c"},
        ]
        rules = generate_base_rules(units)
        cross_rules = [r for r in rules if "affect" in r["trigger"].lower()]
        assert len(cross_rules) == 3


class TestMergeRules:
    def test_manual_rules_override_auto(self):
        auto = [{"trigger": "Agent repeats the same output or action 3+ times", "action": "Stop"}]
        manual = [{"trigger": "Agent repeats the same output or action 3+ times", "action": "Custom action"}]
        merged = merge_rules(auto, manual)
        assert len(merged) == 1
        assert merged[0]["action"] == "Custom action"

    def test_non_overlapping_rules_are_combined(self):
        auto = [{"trigger": "Auto rule A", "action": "Action A"}]
        manual = [{"trigger": "Manual rule B", "action": "Action B"}]
        merged = merge_rules(auto, manual)
        assert len(merged) == 2

    def test_empty_manual_keeps_all_auto(self):
        auto = [
            {"trigger": "Rule 1", "action": "Action 1"},
            {"trigger": "Rule 2", "action": "Action 2"},
        ]
        merged = merge_rules(auto, [])
        assert len(merged) == 2


class TestWorkspaceIsolation:
    def test_generates_directives_per_unit(self):
        units = [
            {"name": "Dev", "purpose": "Build"},
            {"name": "Sales", "purpose": "Sell"},
        ]
        directives = generate_workspace_isolation_rules(units)
        assert len(directives) == 2
        assert directives[0]["agent"] == "Dev"
        assert "s1-dev" in directives[0]["workspace"]
        assert directives[1]["agent"] == "Sales"
        assert "s1-sales" in directives[1]["workspace"]


class TestCommunicationMatrix:
    def test_s1_can_only_talk_to_s2(self):
        matrix = generate_agent_communication_matrix(["s1-dev", "s1-sales"])
        allow = matrix["agentToAgent"]["allow"]
        assert allow["s1-dev"] == ["s2-coordination"]
        assert allow["s1-sales"] == ["s2-coordination"]

    def test_s2_can_talk_to_all(self):
        matrix = generate_agent_communication_matrix(["s1-dev"])
        allow = matrix["agentToAgent"]["allow"]
        s2_targets = allow["s2-coordination"]
        assert "s1-*" in s2_targets
        assert "s3-optimization" in s2_targets
        assert "s4-intelligence" in s2_targets

    def test_s3star_has_readonly_on_s1(self):
        matrix = generate_agent_communication_matrix(["s1-dev"])
        allow = matrix["agentToAgent"]["allow"]
        assert allow["s3star-audit"] == ["s1-*"]

    def test_subagents_configured(self):
        matrix = generate_agent_communication_matrix(["s1-dev"])
        assert "s2-coordination" in matrix["subagents"]["allowAgents"]
        assert "s3-optimization" in matrix["subagents"]["allowAgents"]
