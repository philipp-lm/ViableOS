"""VSM Completeness Checker — evaluates a parsed config against all six systems.

Extended with community-driven checks: token budgets, model warnings,
persistence, workspace isolation, security, and rollout readiness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from viableos.budget import MODEL_WARNINGS


@dataclass
class CheckResult:
    system: str
    name: str
    present: bool
    details: str
    suggestions: list[str] = field(default_factory=list)


@dataclass
class Warning:
    category: str
    severity: str  # "info", "warning", "critical"
    message: str
    suggestion: str = ""


@dataclass
class ViabilityReport:
    score: int
    total: int
    checks: list[CheckResult]
    warnings: list[Warning] = field(default_factory=list)


def _check_s1(vs: dict[str, Any]) -> CheckResult:
    units = vs.get("system_1", [])
    if units:
        names = ", ".join(u.get("name", "?") for u in units)
        return CheckResult(
            system="S1",
            name="Operations",
            present=True,
            details=f"{len(units)} unit{'s' if len(units) != 1 else ''}: {names}",
        )
    return CheckResult(
        system="S1",
        name="Operations",
        present=False,
        details="No operational units defined",
        suggestions=["Define at least one operational unit"],
    )


def _check_s2(vs: dict[str, Any]) -> CheckResult:
    rules = vs.get("system_2", {}).get("coordination_rules", [])
    if rules:
        return CheckResult(
            system="S2",
            name="Coordination",
            present=True,
            details=f"{len(rules)} rule{'s' if len(rules) != 1 else ''} defined",
        )
    return CheckResult(
        system="S2",
        name="Coordination",
        present=False,
        details="No coordination rules defined",
        suggestions=["Add coordination rules to prevent agent conflicts"],
    )


def _check_s3(vs: dict[str, Any]) -> CheckResult:
    s3 = vs.get("system_3", {})
    fields = [k for k in ("reporting_rhythm", "resource_allocation") if s3.get(k)]
    if fields:
        parts = []
        if s3.get("reporting_rhythm"):
            parts.append(f"{s3['reporting_rhythm'].capitalize()} reporting")
        if s3.get("resource_allocation"):
            parts.append("resource allocation set")
        return CheckResult(
            system="S3",
            name="Optimization",
            present=True,
            details=", ".join(parts),
        )
    return CheckResult(
        system="S3",
        name="Optimization",
        present=False,
        details="No optimization configuration defined",
        suggestions=["Add resource allocation or reporting rhythm"],
    )


def _check_s3_star(vs: dict[str, Any]) -> CheckResult:
    checks = vs.get("system_3_star", {}).get("checks", [])
    if checks:
        names = ", ".join(c.get("name", "?") for c in checks)
        return CheckResult(
            system="S3*",
            name="Audit",
            present=True,
            details=f"{len(checks)} check{'s' if len(checks) != 1 else ''}: {names}",
        )
    return CheckResult(
        system="S3*",
        name="Audit",
        present=False,
        details="No audit checks defined",
        suggestions=["Add audit checks \u2014 don't trust agent self-reports"],
    )


def _check_s4(vs: dict[str, Any]) -> CheckResult:
    monitoring = vs.get("system_4", {}).get("monitoring", {})
    fields = [
        k for k in ("competitors", "technology", "regulation") if monitoring.get(k)
    ]
    if fields:
        return CheckResult(
            system="S4",
            name="Intelligence",
            present=True,
            details=f"Monitoring: {', '.join(fields)}",
        )
    return CheckResult(
        system="S4",
        name="Intelligence",
        present=False,
        details="No environment monitoring defined",
        suggestions=[
            "Add environment monitoring (competitors, technology, regulation)"
        ],
    )


def _check_s5(vs: dict[str, Any]) -> CheckResult:
    identity = vs.get("identity", {})
    purpose = identity.get("purpose", "").strip()
    if purpose:
        return CheckResult(
            system="S5",
            name="Identity",
            present=True,
            details=f'Purpose: "{purpose}"',
        )
    return CheckResult(
        system="S5",
        name="Identity",
        present=False,
        details="No purpose defined",
        suggestions=["Define your system's purpose and values"],
    )


# ── Community-driven warnings ───────────────────────────────────────────────


def _check_token_budget(vs: dict[str, Any]) -> list[Warning]:
    """Painpoint #1: Token costs are the #1 issue."""
    warnings = []
    budget = vs.get("budget", {})
    if not budget.get("monthly_usd"):
        warnings.append(Warning(
            category="Token Budget",
            severity="critical",
            message="No token budget defined. Without limits, costs can spiral out of control.",
            suggestion="Set a monthly budget in Step 3. Even $50/month with 'frugal' strategy is better than nothing.",
        ))
    elif not budget.get("alerts"):
        warnings.append(Warning(
            category="Token Budget",
            severity="warning",
            message="Budget set but no alerts configured. You won't know when you're overspending.",
            suggestion="Add budget alerts (e.g. warn at 80%, auto-downgrade at 95%).",
        ))
    return warnings


def _check_model_warnings(vs: dict[str, Any]) -> list[Warning]:
    """Painpoint #5: Model choice is critical — warn about known issues."""
    warnings = []
    routing = vs.get("model_routing", {})
    units = vs.get("system_1", [])

    models_in_use: set[str] = set()
    for unit in units:
        if unit.get("model"):
            models_in_use.add(unit["model"])
    for key, model in routing.items():
        if key != "provider_preference" and model:
            models_in_use.add(model)

    for model_id in models_in_use:
        if model_id in MODEL_WARNINGS:
            warnings.append(Warning(
                category="Model Warning",
                severity="warning",
                message=f"{model_id}: {MODEL_WARNINGS[model_id]}",
                suggestion="Consider switching to a model with 'excellent' agent reliability for production use.",
            ))

    return warnings


def _check_persistence(vs: dict[str, Any]) -> list[Warning]:
    """Painpoint #3: Sessions don't survive restarts without persistence."""
    warnings = []
    persistence = vs.get("persistence", {})
    strategy = persistence.get("strategy", "none")
    if strategy == "none" or not persistence:
        warnings.append(Warning(
            category="Persistence",
            severity="warning",
            message="No persistence strategy defined. Agent state is lost when sessions end.",
            suggestion="Configure persistence (sqlite or file) so agents can resume work across sessions.",
        ))
    return warnings


def _check_security(vs: dict[str, Any]) -> list[Warning]:
    """Painpoint #7: Multi-agent trust and tool scoping."""
    warnings = []
    units = vs.get("system_1", [])
    has_s3star = bool(vs.get("system_3_star", {}).get("checks"))

    sensitive_tools = {"ssh", "deployment", "docker", "payment-processing", "customer-data", "database"}
    units_with_sensitive = []
    for unit in units:
        tools = set(unit.get("tools", []))
        overlap = tools & sensitive_tools
        if overlap:
            units_with_sensitive.append((unit.get("name", "?"), overlap))

    if units_with_sensitive and not has_s3star:
        names = ", ".join(f"{n} ({', '.join(t)})" for n, t in units_with_sensitive)
        warnings.append(Warning(
            category="Security",
            severity="critical",
            message=f"Agents with sensitive tools but NO S3* Audit: {names}",
            suggestion="Add audit checks — agents with sensitive tool access need independent verification.",
        ))

    routing = vs.get("model_routing", {})
    s1_routine = routing.get("s1_routine", "")
    s3star_audit = routing.get("s3_star_audit", "")
    if s1_routine and s3star_audit:
        s1_provider = s1_routine.split("/")[0]
        s3star_provider = s3star_audit.split("/")[0]
        if s1_provider == s3star_provider and has_s3star:
            warnings.append(Warning(
                category="Security",
                severity="warning",
                message=f"S1 and S3* Auditor use the same provider ({s1_provider}). Correlated errors are likely.",
                suggestion="Use a different provider for the Auditor to catch hallucinations the S1 models miss.",
            ))

    never_do = vs.get("identity", {}).get("never_do", [])
    if not never_do:
        warnings.append(Warning(
            category="Security",
            severity="info",
            message="No 'never do' boundaries defined for agents.",
            suggestion="Define what agents should NEVER do (e.g. 'delete production data', 'send emails without approval').",
        ))

    return warnings


def _check_coordination_rules(vs: dict[str, Any]) -> list[Warning]:
    """Painpoint #2 & #4: Agents need rules and workspace isolation.

    Checks both manual rules AND auto-generated rules (which are always
    added at package generation time).
    """
    from viableos.coordination import generate_base_rules, merge_rules

    warnings = []
    units = vs.get("system_1", [])
    manual_rules = vs.get("system_2", {}).get("coordination_rules", [])

    auto_rules = generate_base_rules(units) if units else []
    all_rules = merge_rules(auto_rules, manual_rules)

    if len(units) >= 2 and not manual_rules:
        warnings.append(Warning(
            category="Coordination",
            severity="info",
            message=f"You have {len(units)} units with no custom coordination rules. Auto-generated rules ({len(auto_rules)}) will be used.",
            suggestion="Consider adding custom rules specific to your workflow in addition to the auto-generated base rules.",
        ))

    has_anti_loop = any(
        "loop" in r.get("trigger", "").lower() or "repeat" in r.get("trigger", "").lower()
        for r in all_rules
    )
    if not has_anti_loop:
        warnings.append(Warning(
            category="Coordination",
            severity="warning",
            message="No anti-looping rule found. Agents commonly get stuck repeating the same output.",
            suggestion="Add a rule: 'Agent repeats output 3+ times → stop and escalate'.",
        ))

    return warnings


def _check_rollout_readiness(vs: dict[str, Any]) -> list[Warning]:
    """Painpoint #6: The gap between demo and reality."""
    warnings = []
    units = vs.get("system_1", [])
    has_rules = bool(vs.get("system_2", {}).get("coordination_rules"))
    has_hitl = bool(vs.get("human_in_the_loop", {}).get("approval_required"))

    if len(units) > 3 and not has_rules:
        warnings.append(Warning(
            category="Rollout",
            severity="warning",
            message=f"You're starting with {len(units)} agents at once. Community experience: start with 1-2.",
            suggestion="Consider starting with your most important unit, get it working end-to-end, then add more.",
        ))

    if not has_hitl:
        warnings.append(Warning(
            category="Rollout",
            severity="warning",
            message="No human-in-the-loop approvals configured.",
            suggestion="Define which actions need your approval. Start strict, loosen as you build trust.",
        ))

    return warnings


def check_viability(config: dict[str, Any]) -> ViabilityReport:
    """Run all six VSM checks plus community-driven warnings."""
    vs = config.get("viable_system", {})
    checks = [
        _check_s1(vs),
        _check_s2(vs),
        _check_s3(vs),
        _check_s3_star(vs),
        _check_s4(vs),
        _check_s5(vs),
    ]
    score = sum(1 for c in checks if c.present)

    warnings: list[Warning] = []
    warnings.extend(_check_token_budget(vs))
    warnings.extend(_check_model_warnings(vs))
    warnings.extend(_check_persistence(vs))
    warnings.extend(_check_security(vs))
    warnings.extend(_check_coordination_rules(vs))
    warnings.extend(_check_rollout_readiness(vs))

    return ViabilityReport(score=score, total=6, checks=checks, warnings=warnings)
