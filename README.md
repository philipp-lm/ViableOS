# ViableOS

**The operating system for viable AI agent organizations.**

ViableOS applies the [Viable System Model](https://en.wikipedia.org/wiki/Viable_system_model) (VSM) to multi-agent AI systems. Instead of building a flat list of agents, you define a self-governing organization with operations, coordination, optimization, audit, intelligence, and policy — then deploy it to [OpenClaw](https://github.com/openclaw).

## What it does

1. **Guided Setup Wizard** — 5-step web wizard walks you through identity, team structure, budget, models, and human-in-the-loop configuration
2. **Organization Templates** — Start from SaaS Startup, E-Commerce, Freelance/Agency, Content Creator, or Personal Productivity
3. **Smart Budget Calculator** — Maps your monthly USD budget to per-agent model allocations (frugal / balanced / performance)
4. **SOUL.md Generator** — Creates personality files for every agent with roles, boundaries, coordination rules, and values
5. **OpenClaw Package** — Generates a complete deployment package (`openclaw.json`, `install.sh`, agent workspaces)
6. **Visual Dashboard** — VSM system map, budget donut, model routing chart, agent cards, HiTL summary
7. **VSM Completeness Checker** — Validates your config against all 6 VSM systems with actionable suggestions

## Quick Start

```bash
# Install
pip install -e .

# Launch the web app
viableos app

# Or use the CLI
viableos init                          # Generate a starter config
viableos check viableos.yaml           # Check VSM completeness
viableos generate viableos.yaml        # Generate OpenClaw package
```

## Web App

The web app at `http://localhost:8501` provides:

- **Setup Wizard** — Identity → Template → Customize Teams → Budget & Models → Human-in-the-Loop
- **Dashboard** — Live VSM overview, budget allocation chart, model routing, agent cards, export
- **Demo Mode** — Click any template in the sidebar to see a fully configured system instantly

## Organization Templates

| Template | Units | Best for |
|---|---|---|
| SaaS Startup | Product Dev, Operations, Go-to-Market | Technical founders |
| E-Commerce | Sourcing, Store, Fulfillment, Customer Service | Online retailers |
| Freelance/Agency | Client Acquisition, Delivery, Knowledge | Solo consultants |
| Content Creator | Production, Community, Monetization | YouTubers, writers |
| Personal Productivity | Deep Work, Admin, Learning | Anyone |

## VSM Systems

| System | Role | Agent |
|---|---|---|
| S1 | Operations — the units that do the actual work | Your custom units |
| S2 | Coordination — prevents conflicts between units | Coordinator |
| S3 | Optimization — allocates resources, weekly digest | Optimizer |
| S3* | Audit — independent quality checks (different AI provider) | Auditor |
| S4 | Intelligence — monitors environment, strategic briefs | Scout |
| S5 | Identity — enforces values, prepares human decisions | Policy Guardian |

## Budget Strategies

| Strategy | S1 Routine | S1 Complex | S3 Optimizer | S4 Scout |
|---|---|---|---|---|
| Frugal | Haiku | Haiku | Haiku | Sonnet |
| Balanced | Haiku | Sonnet | Sonnet | Opus |
| Performance | Sonnet | Opus | Opus | Opus |

The Auditor (S3*) always uses a different provider than S1 to prevent correlated hallucinations.

## Human-in-the-Loop

Three levels of human involvement:
- **Approval Required** — Agent stops and waits for your OK
- **Review Required** — Agent proceeds but sends results for your review
- **Emergency Alerts** — Interrupts you immediately (data leak, security, budget exceeded)

## CLI Reference

```
viableos --version           # Show version
viableos init                # Generate starter YAML
viableos check <file>        # VSM completeness report
viableos generate <file>     # Generate OpenClaw package
viableos app                 # Launch web wizard + dashboard
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check src/ tests/
```

## Roadmap

- [x] v0.1 — YAML schema, checker, CLI
- [x] v0.2 — Web wizard, dashboard, budget calculator, OpenClaw generator, templates
- [ ] v0.3 — Live agent monitoring, real OpenClaw integration
- [ ] v0.4 — Multi-runtime support (LangGraph, CrewAI)

## License

MIT
