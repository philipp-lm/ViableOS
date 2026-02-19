# ViableOS

**The operating system for viable AI agent organizations.**

ViableOS applies [Stafford Beer's Viable System Model](https://en.wikipedia.org/wiki/Viable_system_model) — a 50-year proven organizational theory from management cybernetics — to AI multi-agent systems.

You describe your business. We organize your agents.

---

## The Problem

Every multi-agent framework gives you building blocks: agents, tools, routing. None of them tells you **how to organize** your agents.

The result? 40% of multi-agent projects get scaled back or abandoned (Deloitte 2025) — not because the agents are bad, but because the *organization* is missing.

## The Solution

ViableOS provides the five control functions every agent system needs:

```
┌─────────────────────────────────────────────────┐
│  S5  Identity     — Purpose, values, policies   │
│  S4  Intelligence — Outside & future monitoring  │
│  S3  Optimization — Resource allocation, synergy │
│  S3* Audit        — Independent quality checks   │
│  S2  Coordination — Conflict prevention, sync    │
│  S1  Operations   — Your actual working agents   │
├─────────────────────────────────────────────────┤
│  Backends: OpenClaw │ LangGraph │ CrewAI │ ...  │
└─────────────────────────────────────────────────┘
```

## How It Works

1. **Define your identity** — What is your system for? What are your values?
2. **Identify operational units** — Guided segmentation of your S1 agents
3. **Auto-generate the control system** — Coordination rules, KPIs, audit checks, intelligence scope
4. **Deploy** — ViableOS generates agent configurations for your backend
5. **Monitor** — Live dashboard detects organizational pathologies before they become failures

## Configuration (Preview)

```yaml
viable_system:
  name: "My SaaS Business"

  identity:
    purpose: "Help therapists focus on patients, not paperwork"
    values:
      - "Privacy above everything"
      - "Simplicity over feature bloat"

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
      - trigger: "Product Development deploys new feature"
        action: "Notify Go-to-Market for website update"
```

## Features

| Feature | Status |
|---------|--------|
| VSM Configuration DSL (YAML) | 🔜 Coming soon |
| CLI: `viableos init` | 🔜 Coming soon |
| OpenClaw Adapter | 🔜 Coming soon |
| Industry Templates | 🔜 Coming soon |
| Web Dashboard | 📋 Planned |
| Pathology Detection Engine | 📋 Planned |
| Recursion Engine | 📋 Planned |
| LangGraph / CrewAI Adapters | 📋 Planned |

## Why VSM?

No existing multi-agent framework implements all five control functions:

```
                        S1    S2    S3    S3*   S4    S5
                       Ops  Coord Optim Audit Intel Ident
───────────────────────────────────────────────────────────
CrewAI (Hierarchy)      ✅    ❌    ⚠️    ❌    ❌    ❌
OpenAI Swarm            ✅    ❌    ❌    ❌    ❌    ❌
AutoGen (Group Chat)    ⚠️    ⚠️    ❌    ❌    ❌    ❌
LangGraph (Supervisor)  ✅    ❌    ⚠️    ❌    ❌    ❌
───────────────────────────────────────────────────────────
ViableOS                ✅    ✅    ✅    ✅    ✅    ✅
```

Every incomplete system develops **organizational pathologies** — predictable failures that worsen over time. ViableOS is the first framework designed to prevent them.

## Blog Series: The 7 Pathologies of AI Agent Teams

1. [Your AI Agents Need an Org Chart — But Not the Kind You Think](#) *(coming soon)*
2. The Dominance Problem: When One Agent Eats All Your Tokens
3. Nobody's Watching: Why Your System Needs an Auditor
4. Stuck in the Present: The Missing Intelligence Function
5. The Coordination Tax: How Agent Communication Goes Wrong
6. Multiple Personalities: When Agents Have No Shared Purpose
7. From Chaos to Viable: The Fix

## Theoretical Foundation

- **Stafford Beer** — *Brain of the Firm* (1972)
- **Martin Pfiffner** — *Die dritte Dimension des Organisierens* (Springer, 2020)
- 50+ years of validation across biology, corporations, and governments
- The only organizational model proven to be both necessary and sufficient for viability

## About the Author

**Philipp Enderle** — Engineer turned strategy consultant turned founder.

Background: Mechanical Engineering (KIT, B.Sc.) and Engineering & Management (TU Munich, M.Sc., UC Berkeley). Then 7+ years of strategy consulting at Deloitte and Berylls by AlixPartners — designing organizational transformations, target operating models, and digital agile organizations for DAX automotive OEMs (800+ FTE scope).

After seeing the same structural pathologies in AI agent systems that I'd diagnosed in billion-dollar companies — missing coordination, no audit, zero strategic foresight — I started building ViableOS to bridge organizational cybernetics with multi-agent AI. My own healthcare SaaS ([Mola](https://github.com/philipp-lm/mola_app)) serves as the first production test case.

- [LinkedIn](https://www.linkedin.com/in/philipp-enderle/)
- [GitHub](https://github.com/philipp-lm)

## Get Involved

⭐ Star this repo to follow progress

📬 [Subscribe to the newsletter](https://viableos.dev) for updates

🐛 [Open an issue](../../issues) to share your multi-agent organization challenges

## License

MIT — see [LICENSE](LICENSE) for details.

---

*"There are many possible manifestations. There is one cybernetic solution."*
— Stafford Beer
