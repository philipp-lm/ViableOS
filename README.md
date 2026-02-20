# ViableOS

> Orchestration layer for multi-agent AI systems, based on [Stafford Beer's Viable System Model](https://en.wikipedia.org/wiki/Viable_system_model) (VSM).

**Status: v0.1 — Config schema + CLI available.** Star/watch to follow along.

---

## What is this?

Multi-agent frameworks (LangGraph, CrewAI, OpenAI Agents SDK, ...) give you agents, tools, and routing. They don't give you an organizational structure — who coordinates whom, who audits what, how to balance short-term execution with long-term adaptation.

ViableOS adds that layer. It sits on top of your existing agent framework and provides the six control functions from VSM:

```
┌──────────────────────────────────────────────┐
│  S5  Identity      Purpose, values, policies │
│  S4  Intelligence  Environment monitoring    │
│  S3  Optimization  Resource allocation       │
│  S3* Audit         Independent verification  │
│  S2  Coordination  Conflict prevention       │
│  S1  Operations    Your actual agents        │
├──────────────────────────────────────────────┤
│  Runtime: OpenClaw · LangGraph · CrewAI      │
│  LLMs:    Anthropic · OpenAI · Ollama · ...  │
└──────────────────────────────────────────────┘
```

Framework-agnostic (pluggable runtime adapters). LLM-agnostic (any provider per system). Runs locally with Ollama or in the cloud.

## Config example

```yaml
viable_system:
  name: "My SaaS"
  runtime: "openclaw"        # or: langgraph, crewai, openai-agents, cursor

  identity:
    purpose: "Help therapists focus on patients, not paperwork"
    values: ["Privacy above everything", "Simplicity over feature bloat"]

  system_1:
    - name: "Product Development"
      purpose: "Build and stabilize the software"
      autonomy: "Can fix bugs independently. Features need approval."
      tools: [github, ci-cd, testing]

    - name: "Go-to-Market"
      purpose: "Acquire first customers"
      autonomy: "Can draft content independently. Publishing needs approval."
      tools: [website-editing, seo-analysis, copywriting]

  system_2:
    coordination_rules:
      - trigger: "Go-to-Market promises feature on website"
        action: "Validate with Product Development before publishing"

  system_3_star:
    checks:
      - target: "Go-to-Market"
        method: "Compare website claims against shipped features"
```

## Install

```bash
git clone https://github.com/philipp-lm/ViableOS.git
cd ViableOS
pip install -e .
```

## Usage

```bash
# Generate a starter config
viableos init

# Check your config against VSM principles
viableos check viableos.yaml
```

Example output:

```
━━━ ViableOS Viability Check ━━━

  ✅ S1  Operations     3 units: Product Development, Operations, Go-to-Market
  ✅ S2  Coordination   3 rules defined
  ✅ S3  Optimization   Weekly reporting, resource allocation set
  ✅ S3* Audit          3 checks: Code Quality, Content Accuracy, GDPR Compliance
  ✅ S4  Intelligence   Monitoring: competitors, technology, regulation
  ✅ S5  Identity       Purpose: "Help therapists focus on patients, not paperwork"

Viability Score: 6/6 — Your system is fully viable.
```

See [`examples/healthcare-saas.yaml`](examples/healthcare-saas.yaml) for a complete config.

## Roadmap

| Component | Status |
|-----------|--------|
| VSM config schema (YAML) | **v0.1** |
| `viableos init` + `viableos check` CLI | **v0.1** |
| OpenClaw runtime adapter | In progress |
| Pathology detection | Planned |
| Recursion engine (nested VSMs) | Planned |
| LangGraph / CrewAI adapters | Planned |
| Web dashboard | Planned |
| Ollama / local LLM support | Planned |

## Architecture

ViableOS reads a YAML config, validates it against VSM principles, and deploys agents to your runtime of choice. It's a layer between your config and your agent framework — not a replacement.

```
     YAML Config  ──▶  VSM Core  ──▶  Runtime Adapter  ──▶  Your agents
                       (parse,         (OpenClaw,
                        validate)       LangGraph, ...)
```

## Background

VSM was developed by Stafford Beer in the 1970s. It defines the minimal set of control functions any organization needs to remain viable — applicable to companies, governments, and (we think) AI agent teams.

- Beer, S. — *Brain of the Firm* (1972)
- Pfiffner, M. — *Die dritte Dimension des Organisierens* (Springer, 2020)

I'm building this because I ran into the exact same organizational pathologies in my own multi-agent setup (a healthcare SaaS) that I used to diagnose in large corporations as a strategy consultant. More context in the blog series:

1. [Your AI Agents Need an Org Chart — But Not the Kind You Think](https://dev.to/philippenderle/your-ai-agents-need-an-org-chart-but-not-the-kind-you-think-2fg7)

## Contributing

This is early-stage. If you're interested in multi-agent organization, [open an issue](../../issues) or reach out.

- [Newsletter](https://buttondown.com/viableos)
- [Blog series on Dev.to](https://dev.to/philippenderle)

## License

MIT — see [LICENSE](LICENSE).
