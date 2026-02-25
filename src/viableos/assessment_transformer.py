"""Transform an assessment_config.json into a viable_system config for the generator.

The assessment dialog produces a rich JSON with recursion levels, dependencies,
metasystem tasks, shared resources, external forces, etc. This module maps that
into the viable_system schema the generator expects, preserving domain context
that generic wizard-based configs would lack.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _priority_to_weight(priority: int | str) -> int:
    """Map assessment priority (1=highest) to generator weight (1-10, higher = more budget)."""
    mapping = {1: 8, 2: 5, 3: 3}
    if isinstance(priority, int):
        return mapping.get(priority, 5)
    return 5


def _classify_external_force(force: dict[str, Any]) -> str:
    """Classify an external force into competitors/technology/regulation."""
    name_lower = force.get("name", "").lower()
    regulation_keywords = [
        "sgb", "dsgvo", "datenschutz", "compliance", "gesetz", "recht",
        "verordnung", "regulation", "vergütung", "§",
    ]
    tech_keywords = [
        "technolog", "llm", "ki", "ai", "algorithm", "software", "api",
    ]
    competition_keywords = [
        "wettbew", "konkur", "compet", "markt", "market",
    ]
    for kw in regulation_keywords:
        if kw in name_lower:
            return "regulation"
    for kw in tech_keywords:
        if kw in name_lower:
            return "technology"
    for kw in competition_keywords:
        if kw in name_lower:
            return "competitors"
    return "regulation"


def _build_s1_units(assessment: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert recursion levels into a flat S1 unit list with sub_unit metadata."""
    recursion = assessment.get("recursion_levels", {})
    level_0 = recursion.get("level_0", {})
    units_raw = level_0.get("operational_units", [])

    sub_levels = {
        key: val for key, val in recursion.items()
        if key.startswith("level_1")
    }
    parent_to_sublevel: dict[str, dict[str, Any]] = {}
    for sl in sub_levels.values():
        parent_id = sl.get("parent", "")
        if parent_id:
            parent_to_sublevel[parent_id] = sl

    s1_units: list[dict[str, Any]] = []
    for unit in units_raw:
        uid = unit.get("id", "")
        entry: dict[str, Any] = {
            "name": unit.get("name", uid),
            "purpose": unit.get("description", ""),
            "weight": _priority_to_weight(unit.get("priority", 2)),
        }

        if uid in parent_to_sublevel:
            sl = parent_to_sublevel[uid]
            sub_units = []
            for su in sl.get("operational_units", []):
                sub_units.append({
                    "name": su.get("name", su.get("id", "")),
                    "purpose": su.get("description", ""),
                    "priority": su.get("priority", 2),
                })
            entry["sub_units"] = sub_units

            central = sl.get("central_object")
            if central:
                entry["domain_context"] = (
                    f"Central object: {central['name']} "
                    f"({central.get('flow', '')})"
                )

        s1_units.append(entry)

    return s1_units


def _build_dependencies(assessment: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract business-level dependencies as structured list."""
    deps_raw = assessment.get("dependencies", {})
    result: list[dict[str, Any]] = []

    for dep in deps_raw.get("business_level", []):
        result.append({
            "from": dep.get("from", ""),
            "to": dep.get("to", ""),
            "description": dep.get("what", ""),
        })

    return result


def _build_domain_flow(assessment: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the central object flow if present."""
    deps = assessment.get("dependencies", {})
    pf = deps.get("product_flow")
    if not pf:
        return None
    return {
        "central_object": pf.get("central_object", ""),
        "flow_description": pf.get("direction", ""),
        "feedback_loop": pf.get("feedback_loop", ""),
    }


def _build_coordination_rules(assessment: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert S2 tasks + dependencies into coordination rules."""
    rules: list[dict[str, Any]] = []

    meta_s2 = assessment.get("metasystem", {}).get("s2_coordination", {})
    for task in meta_s2.get("tasks", []):
        rules.append({
            "trigger": f"Coordination needed for: {task}",
            "action": f"Coordinator handles {task} according to defined process",
        })

    for dep in assessment.get("dependencies", {}).get("business_level", []):
        rules.append({
            "trigger": f"{dep['from']} produces output affecting {dep['to']}",
            "action": f"Coordinator routes: {dep.get('what', 'information')}",
        })

    return rules


def _build_s3_config(assessment: dict[str, Any]) -> dict[str, Any]:
    """Map S3 optimization tasks to reporting and resource config."""
    meta_s3 = assessment.get("metasystem", {}).get("s3_optimization", {})
    tasks = meta_s3.get("tasks", [])

    kpi_list = [t for t in tasks if "kpi" in t.lower() or "tracking" in t.lower()]
    resource_tasks = [t for t in tasks if t not in kpi_list]

    return {
        "reporting_rhythm": "weekly",
        "resource_allocation": "; ".join(resource_tasks) if resource_tasks else "",
        "kpi_list": tasks,
        "label": meta_s3.get("label", "Optimizer"),
    }


def _build_s3star_config(assessment: dict[str, Any]) -> dict[str, Any]:
    """Map S3* audit tasks to checks."""
    meta = assessment.get("metasystem", {}).get("s3_star_audit", {})
    checks = []
    for task in meta.get("tasks", []):
        checks.append({
            "name": task,
            "target": "all_units",
            "method": "independent_verification",
        })
    result: dict[str, Any] = {"checks": checks}
    if meta.get("design_principle"):
        result["on_failure"] = meta["design_principle"]
    result["label"] = meta.get("label", "Auditor")
    return result


def _build_s4_config(assessment: dict[str, Any]) -> dict[str, Any]:
    """Map S4 tasks + external forces to monitoring config."""
    meta = assessment.get("metasystem", {}).get("s4_intelligence", {})
    forces = assessment.get("external_forces", [])

    competitors: list[str] = []
    technology: list[str] = []
    regulation: list[str] = []

    for task in meta.get("tasks", []):
        cat = _classify_external_force({"name": task})
        {"competitors": competitors, "technology": technology, "regulation": regulation}[cat].append(task)

    for force in forces:
        cat = _classify_external_force(force)
        entry = force["name"]
        if force.get("frequency"):
            entry += f" ({force['frequency']})"
        target = {"competitors": competitors, "technology": technology, "regulation": regulation}[cat]
        if entry not in target:
            target.append(entry)

    return {
        "monitoring": {
            "competitors": competitors,
            "technology": technology,
            "regulation": regulation,
        },
        "label": meta.get("label", "Scout"),
    }


def _build_identity(assessment: dict[str, Any]) -> dict[str, Any]:
    """Build identity from purpose + S5 policies."""
    meta_s5 = assessment.get("metasystem", {}).get("s5_policy", {})
    policies = meta_s5.get("policies", [])

    values = [p for p in policies if not p.lower().startswith("ethik")]
    never_do_raw = [p for p in policies if p.lower().startswith("ethik")]

    identity: dict[str, Any] = {
        "purpose": assessment.get("purpose", ""),
        "values": values,
    }
    if never_do_raw:
        identity["never_do"] = never_do_raw

    return identity


def _build_hitl(assessment: dict[str, Any]) -> dict[str, Any]:
    """Set human-in-the-loop defaults based on team size."""
    team = assessment.get("team", {})
    size = team.get("size", 1)

    hitl: dict[str, Any] = {
        "notification_channel": "whatsapp",
        "approval_required": ["deployment", "budget_changes", "new_agent_creation"],
    }

    if size <= 2:
        hitl["approval_required"].extend([
            "customer_communication",
            "data_deletion",
        ])

    return hitl


def transform_assessment(assessment: dict[str, Any]) -> dict[str, Any]:
    """Convert an assessment_config.json dict into a viable_system config.

    Returns a dict compatible with the ViableOS schema, enriched with
    domain-specific fields from the assessment.
    """
    s1_units = _build_s1_units(assessment)
    dependencies = _build_dependencies(assessment)
    domain_flow = _build_domain_flow(assessment)
    coord_rules = _build_coordination_rules(assessment)
    s3_config = _build_s3_config(assessment)
    s3star_config = _build_s3star_config(assessment)
    s4_config = _build_s4_config(assessment)
    identity = _build_identity(assessment)
    hitl = _build_hitl(assessment)

    success_criteria = assessment.get("success_criteria", [])
    shared_resources = assessment.get("shared_resources", [])

    config: dict[str, Any] = {
        "viable_system": {
            "name": assessment.get("system_name", "Unnamed System"),
            "identity": identity,
            "system_1": s1_units,
            "system_2": {"coordination_rules": coord_rules},
            "system_3": s3_config,
            "system_3_star": s3star_config,
            "system_4": s4_config,
            "human_in_the_loop": hitl,
            "budget": {
                "monthly_usd": 150.0,
                "strategy": "balanced",
            },
            "success_criteria": success_criteria,
            "shared_resources": shared_resources,
        },
    }

    if domain_flow:
        config["viable_system"]["domain_flow"] = domain_flow

    if dependencies:
        config["viable_system"]["dependencies"] = dependencies

    return config


def load_assessment(path: str | Path) -> dict[str, Any]:
    """Load an assessment_config.json file."""
    with open(path) as f:
        return json.load(f)
