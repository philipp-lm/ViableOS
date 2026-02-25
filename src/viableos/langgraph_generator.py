"""LangGraph deployment package generator.

Generates a LangGraph Platform-compatible Python package from a ViableOS config.
Reuses content generators from soul_templates.py and generator.py, but produces
a StateGraph-based Python package instead of OpenClaw markdown files.

Generated package structure:
  viableos-langgraph/
  ├── graph.py              # StateGraph definition
  ├── state.py              # TypedDict State schema
  ├── agents/
  │   ├── s1_<name>/system_prompt.md, skills.md, heartbeat.md
  │   ├── s2_coordination/...
  │   ├── s3_optimization/...
  │   ├── s3star_audit/...
  │   ├── s4_intelligence/...
  │   └── s5_policy/...
  ├── shared/org_memory.md, coordination_rules.md
  ├── requirements.txt
  ├── langgraph.json
  └── .env.example
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from viableos.budget import calculate_budget, get_fallback_chain
from viableos.coordination import (
    generate_base_rules,
    generate_dependency_rules,
    generate_shared_resource_rules,
    merge_rules,
)
from viableos.soul_templates import (
    generate_org_memory,
    generate_s1_soul,
    generate_s2_soul,
    generate_s3_soul,
    generate_s3star_soul,
    generate_s4_soul,
    generate_s5_soul,
)


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_").replace("&", "and")


def _model_to_langchain(model: str) -> tuple[str, str]:
    """Convert a ViableOS model ID to (langchain_class, model_name).

    Returns (ChatClass, model_name) for import in generated code.
    """
    if model.startswith("claude") or "anthropic" in model.lower():
        return "ChatAnthropic", model
    if model.startswith("gpt") or model.startswith("o3") or "openai" in model.lower():
        return "ChatOpenAI", model
    if model.startswith("gemini") or "google" in model.lower():
        return "ChatGoogleGenerativeAI", model
    if model.startswith("deepseek"):
        return "ChatOpenAI", model  # DeepSeek uses OpenAI-compatible API
    if model.startswith("grok"):
        return "ChatOpenAI", model  # xAI uses OpenAI-compatible API
    # Default to OpenAI-compatible
    return "ChatOpenAI", model


def _generate_state_py(s1_units: list[dict[str, Any]]) -> str:
    """Generate the TypedDict State schema for the graph."""
    unit_names = [_slugify(u.get("name", f"unit_{i}")) for i, u in enumerate(s1_units)]

    unit_status_fields = "\n".join(
        f'    {name}_status: str' for name in unit_names
    )

    return f'''"""State schema for the ViableOS LangGraph deployment."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state across all agent nodes."""

    # Message history (append-only)
    messages: Annotated[list, add_messages]

    # Current task being processed
    current_task: str

    # Which agent should act next
    next_agent: str

    # S1 unit statuses
{unit_status_fields}

    # S2 coordination state
    coordination_queue: list[dict]
    active_conflicts: list[dict]

    # S3 optimization state
    budget_status: dict
    performance_metrics: dict

    # S3* audit findings
    audit_findings: list[dict]

    # S4 intelligence signals
    intelligence_signals: list[dict]

    # S5 policy decisions
    pending_decisions: list[dict]
    decision_log: list[dict]

    # Human-in-the-loop
    needs_human_input: bool
    human_feedback: str
'''


def _generate_graph_py(
    config: dict[str, Any],
    s1_units: list[dict[str, Any]],
    plan: Any,
) -> str:
    """Generate the StateGraph definition."""
    vs = config.get("viable_system", {})
    system_name = vs.get("name", "ViableOS System")
    hitl = vs.get("human_in_the_loop", {})
    approval_required = hitl.get("approval_required", [])

    unit_slugs = [_slugify(u.get("name", f"unit_{i}")) for i, u in enumerate(s1_units)]
    unit_names = [u.get("name", f"Unit {i+1}") for i, u in enumerate(s1_units)]

    # Determine model classes needed
    model_classes: set[str] = set()
    model_assignments: list[tuple[str, str, str]] = []  # (node_name, class, model)

    for i, unit in enumerate(s1_units):
        model = unit.get("model") or plan.model_routing.get("s1_routine", "claude-sonnet-4-6")
        cls, m = _model_to_langchain(model)
        model_classes.add(cls)
        model_assignments.append((f"s1_{unit_slugs[i]}", cls, m))

    for system_key, node_name in [
        ("s2_coordination", "s2_coordinator"),
        ("s3_optimization", "s3_optimizer"),
        ("s3_star_audit", "s3star_auditor"),
        ("s4_intelligence", "s4_scout"),
        ("s5_preparation", "s5_policy"),
    ]:
        model = plan.model_routing.get(system_key, "claude-sonnet-4-6")
        cls, m = _model_to_langchain(model)
        model_classes.add(cls)
        model_assignments.append((node_name, cls, m))

    # Build imports
    imports = ["from langchain_anthropic import ChatAnthropic"] if "ChatAnthropic" in model_classes else []
    if "ChatOpenAI" in model_classes:
        imports.append("from langchain_openai import ChatOpenAI")
    if "ChatGoogleGenerativeAI" in model_classes:
        imports.append("from langchain_google_genai import ChatGoogleGenerativeAI")

    imports_str = "\n".join(imports)

    # Build model instantiation
    model_inits: list[str] = []
    for node_name, cls, model in model_assignments:
        model_inits.append(f'    "{node_name}": {cls}(model="{model}"),')
    model_inits_str = "\n".join(model_inits)

    # Build node functions
    node_functions: list[str] = []
    all_node_names: list[str] = []

    for i, slug in enumerate(unit_slugs):
        node_name = f"s1_{slug}"
        all_node_names.append(node_name)
        node_functions.append(f'''
def {node_name}(state: AgentState) -> dict:
    """S1 Operational Unit: {unit_names[i]}"""
    prompt_path = Path(__file__).parent / "agents" / "{node_name}" / "system_prompt.md"
    system_prompt = prompt_path.read_text() if prompt_path.exists() else "You are {unit_names[i]}."
    llm = MODELS["{node_name}"]
    response = llm.invoke([
        {{"role": "system", "content": system_prompt}},
        *state["messages"],
    ])
    return {{"messages": [response], "{slug}_status": "completed"}}
''')

    for sys_name, sys_label, sys_desc in [
        ("s2_coordinator", "Coordinator", "Route information between S1 units, prevent conflicts"),
        ("s3_optimizer", "Optimizer", "Monitor performance, allocate resources, generate reports"),
        ("s3star_auditor", "Auditor", "Independent verification of agent outputs"),
        ("s4_scout", "Scout", "Monitor external environment, generate intelligence briefs"),
        ("s5_policy", "Policy Guardian", "Enforce values and policies, prepare decisions for human"),
    ]:
        all_node_names.append(sys_name)
        node_functions.append(f'''
def {sys_name}(state: AgentState) -> dict:
    """{sys_label}: {sys_desc}"""
    prompt_path = Path(__file__).parent / "agents" / "{sys_name}" / "system_prompt.md"
    system_prompt = prompt_path.read_text() if prompt_path.exists() else "You are the {sys_label}."
    llm = MODELS["{sys_name}"]
    response = llm.invoke([
        {{"role": "system", "content": system_prompt}},
        *state["messages"],
    ])
    return {{"messages": [response]}}
''')

    nodes_str = "\n".join(node_functions)

    # Build graph construction
    add_nodes = "\n".join(f'    graph.add_node("{n}", {n})' for n in all_node_names)

    # Build routing logic
    s1_nodes_list = ", ".join(f'"{n}"' for n in all_node_names if n.startswith("s1_"))

    approval_items = ", ".join(f'"{a}"' for a in approval_required) if approval_required else ""
    approval_check = f"""
    APPROVAL_REQUIRED = [{approval_items}]
""" if approval_required else ""

    return f'''"""ViableOS LangGraph deployment — {system_name}

Auto-generated StateGraph implementing VSM topology:
  S5 (Policy) supervises S3 (Optimizer) which supervises S1 units.
  S2 (Coordinator) handles inter-unit communication.
  S3* (Auditor) performs independent verification.
  S4 (Scout) monitors external environment.
"""

from __future__ import annotations

from pathlib import Path

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

{imports_str}

from state import AgentState


# ── Model assignments ────────────────────────────────────────

MODELS = {{
{model_inits_str}
}}

S1_NODES = [{s1_nodes_list}]
{approval_check}

# ── Node functions ───────────────────────────────────────────
{nodes_str}

def supervisor(state: AgentState) -> dict:
    """S3/S5 Supervisor: routes tasks to appropriate agents."""
    next_agent = state.get("next_agent", "")

    # If human input needed, pause
    if state.get("needs_human_input"):
        return {{"next_agent": "__interrupt__"}}

    # Default routing: cycle through S1 units, then meta-systems
    if not next_agent or next_agent == "start":
        return {{"next_agent": S1_NODES[0] if S1_NODES else "s2_coordinator"}}

    return {{"next_agent": next_agent}}


def route_next(state: AgentState) -> str:
    """Determine which node to execute next."""
    next_agent = state.get("next_agent", "")
    if next_agent == "__interrupt__":
        return END
    if next_agent in [{", ".join(f'"{n}"' for n in all_node_names)}]:
        return next_agent
    return END


# ── Graph construction ───────────────────────────────────────

def build_graph() -> StateGraph:
    """Build the ViableOS StateGraph."""
    graph = StateGraph(AgentState)

    # Add all agent nodes
{add_nodes}
    graph.add_node("supervisor", supervisor)

    # Entry point
    graph.set_entry_point("supervisor")

    # Supervisor routes to agents
    graph.add_conditional_edges(
        "supervisor",
        route_next,
        {{{", ".join(f'"{n}": "{n}"' for n in all_node_names)}}},
    )

    # All agents route back to supervisor
{chr(10).join(f'    graph.add_edge("{n}", "supervisor")' for n in all_node_names)}

    return graph


# ── Compiled graph (used by LangGraph Platform) ──────────────

memory = MemorySaver()
graph = build_graph().compile(checkpointer=memory, interrupt_before=["supervisor"])
'''


def _generate_langgraph_json(system_name: str) -> str:
    """Generate langgraph.json Platform config."""
    config = {
        "dependencies": ["."],
        "graphs": {
            "agent": "./graph.py:graph",
        },
        "env": ".env",
    }
    return json.dumps(config, indent=2)


def _generate_requirements_txt() -> str:
    return """langgraph>=0.3
langchain-core>=0.3
langchain-anthropic>=0.3
langchain-openai>=0.3
langchain-google-genai>=2.0
langgraph-checkpoint>=2.0
python-dotenv>=1.0
"""


def _generate_env_example(config: dict[str, Any]) -> str:
    vs = config.get("viable_system", {})
    models_used: set[str] = set()
    for unit in vs.get("system_1", []):
        if unit.get("model"):
            models_used.add(unit["model"])

    lines = ["# ViableOS LangGraph Environment Variables", ""]

    # Always include Anthropic since it's the default
    lines.append("ANTHROPIC_API_KEY=sk-ant-...")
    lines.append("OPENAI_API_KEY=sk-...")
    lines.append("GOOGLE_API_KEY=...")
    lines.append("")
    lines.append("# LangSmith (optional)")
    lines.append("LANGCHAIN_TRACING_V2=true")
    lines.append("LANGCHAIN_API_KEY=ls__...")
    lines.append(f"LANGCHAIN_PROJECT=viableos-{_slugify(vs.get('name', 'system'))}")

    return "\n".join(lines) + "\n"


def generate_langgraph_package(
    config: dict[str, Any],
    output_dir: str | Path,
) -> Path:
    """Generate a complete LangGraph deployment package from a ViableOS config."""
    output = Path(output_dir)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    vs = config.get("viable_system", {})
    identity = vs.get("identity", {})
    hitl = vs.get("human_in_the_loop", {})
    s1_units = vs.get("system_1", [])
    manual_rules = vs.get("system_2", {}).get("coordination_rules", [])
    s3_cfg = vs.get("system_3", {})
    s3star_cfg = vs.get("system_3_star", {})
    s4_cfg = vs.get("system_4", {})
    monitoring = s4_cfg.get("monitoring", {})

    dependencies = vs.get("dependencies", [])
    shared_resources = vs.get("shared_resources", [])
    domain_flow = vs.get("domain_flow")
    success_criteria = vs.get("success_criteria", [])

    # Generate coordination rules
    auto_rules = generate_base_rules(s1_units)
    dep_rules = generate_dependency_rules(dependencies) if dependencies else []
    shared_rules = generate_shared_resource_rules(shared_resources) if shared_resources else []
    coord_rules = merge_rules(auto_rules, manual_rules + dep_rules + shared_rules)

    plan = calculate_budget(config)
    s1_names = [u.get("name", "?") for u in s1_units]

    # ── Generate Python files ──────────────────────────────────

    (output / "state.py").write_text(_generate_state_py(s1_units))
    (output / "graph.py").write_text(_generate_graph_py(config, s1_units, plan))
    (output / "requirements.txt").write_text(_generate_requirements_txt())
    (output / "langgraph.json").write_text(_generate_langgraph_json(vs.get("name", "")))
    (output / ".env.example").write_text(_generate_env_example(config))

    # ── Generate agent prompt directories ──────────────────────

    agents_dir = output / "agents"
    agents_dir.mkdir()

    # S1 units
    for i, unit in enumerate(s1_units):
        name = unit.get("name", f"Unit {i+1}")
        slug = f"s1_{_slugify(name)}"
        agent_dir = agents_dir / slug
        agent_dir.mkdir()

        other_units = [n for n in s1_names if n != name]
        soul = generate_s1_soul(
            unit, identity, coord_rules, hitl, other_units,
            dependencies=dependencies, domain_flow=domain_flow,
        )
        (agent_dir / "system_prompt.md").write_text(soul)

    # S2 Coordinator
    s2_dir = agents_dir / "s2_coordinator"
    s2_dir.mkdir()
    s2_label = vs.get("system_2", {}).get("label", "")
    soul = generate_s2_soul(
        coord_rules, s1_names, identity,
        shared_resources=shared_resources, domain_flow=domain_flow, label=s2_label,
    )
    (s2_dir / "system_prompt.md").write_text(soul)

    # S3 Optimizer
    s3_dir = agents_dir / "s3_optimizer"
    s3_dir.mkdir()
    s3_label = s3_cfg.get("label", "")
    soul = generate_s3_soul(
        identity, s1_names, plan.total_monthly_usd,
        s3_cfg.get("resource_allocation", ""), s3_cfg.get("reporting_rhythm", ""),
        kpi_list=s3_cfg.get("kpi_list"),
        success_criteria=success_criteria if success_criteria else None,
        label=s3_label,
    )
    (s3_dir / "system_prompt.md").write_text(soul)

    # S3* Auditor
    s3star_dir = agents_dir / "s3star_auditor"
    s3star_dir.mkdir()
    s3star_label = s3star_cfg.get("label", "")
    checks = s3star_cfg.get("checks", [])
    on_failure = s3star_cfg.get("on_failure", "Escalate to human immediately")
    soul = generate_s3star_soul(identity, checks, s1_names, on_failure, label=s3star_label)
    (s3star_dir / "system_prompt.md").write_text(soul)

    # S4 Scout
    s4_dir = agents_dir / "s4_scout"
    s4_dir.mkdir()
    s4_label = s4_cfg.get("label", "")
    soul = generate_s4_soul(identity, monitoring, label=s4_label)
    (s4_dir / "system_prompt.md").write_text(soul)

    # S5 Policy Guardian
    s5_dir = agents_dir / "s5_policy"
    s5_dir.mkdir()
    soul = generate_s5_soul(identity, hitl)
    (s5_dir / "system_prompt.md").write_text(soul)

    # ── Shared resources ───────────────────────────────────────

    shared_dir = output / "shared"
    shared_dir.mkdir()

    org_memory = generate_org_memory(config)
    (shared_dir / "org_memory.md").write_text(org_memory)

    rules_md = "# Coordination Rules\n\nAuto-generated + manual rules for this system.\n\n"
    for rule in coord_rules:
        rules_md += f"- **When:** {rule['trigger']}\n  **Then:** {rule['action']}\n\n"
    (shared_dir / "coordination_rules.md").write_text(rules_md)

    return output
