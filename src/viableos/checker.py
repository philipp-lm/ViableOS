"""VSM Completeness Checker — evaluates a parsed config against all six systems."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckResult:
    system: str
    name: str
    present: bool
    details: str
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ViabilityReport:
    score: int
    total: int
    checks: list[CheckResult]


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


def check_viability(config: dict[str, Any]) -> ViabilityReport:
    """Run all six VSM checks against a parsed config and return a report."""
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
    return ViabilityReport(score=score, total=6, checks=checks)
