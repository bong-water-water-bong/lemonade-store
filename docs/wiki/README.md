# Project Wiki: Lemonade Store

## Mission
Define the project/spec contract for local-first Lemonade marketplace plugins
for a tiny ma-and-pa shop. Lemonade App / Lemonade Server (`lemond`) is the
runtime; departments are Podman-packaged plugins.

## Architecture
- **Project/Spec Repo**: Defines decentralized department contracts, each
  department living in its own repository.
- **Marketplace Plugins**: Every department is packaged separately as a Podman
  plugin and wired through `lemond`.
- **Shared Event Envelope**: All departments communicate via `store.event.v1` JSON events.
- **Local-First / Stdlib-Only**: The contract package (`lemonade_store.*`) imports only the Python standard library to ensure maximum portability and reliability.
- **Source of Truth**: The `lemonade-cashier` repository is the source of truth for all checkout transactions.

## Agent Handoff
- **How to Test**: Run `make test`, `make lint`, and `make type`. Python 3.11+ is required.
- **Hot Paths**:
    - `src/lemonade_store/`: Core contract helpers for events and department registries.
    - `examples/tie-dye-farms/`: Reference configuration and sample event logs for the first target business.
    - `docs/DEPARTMENTS.md`: Defines the `owns`, `consumes`, and `emits` contracts for every department.
- **Current Priorities**: 
    - Establishing the frontier of cross-department flows (e.g., accounting consuming cashier events).
    - Ensuring all new event types are properly registered in the department registry.

## Decisions & Gotchas
- **Cash-Only Core**: Explicitly forbids Stripe, card readers, or third-party payment gateways in the core path.
- **Owner Approval Gates**: Any agent action with public reach (e.g., marketing posts) or financial consequences must be gated by explicit owner approval in the event log.
- **Privacy Boundary**: No customer card data, audio, or images are to be persisted or processed.
- **Envelope Validation**: The `payload` of an event is opaque to the envelope validator; individual departments are responsible for internal schema validation.
- **No Runtime Dependencies**: Do not add third-party dependencies to the runtime package. External agent bridge packages such as `lemonade-agents`, GAIA, and Torch belong behind the optional `agents` extra so `make install` and contract checks stay lightweight.
- **No App Runtime Here**: Do not launch `lemond`, bind `13305`, or add app
  service/container files to this repo. Plugin packaging belongs in
  `lemonade-marketplace-plugins`.


## OpenSpec Workflow

Use `openspec/` as the working standard for department changes:

- `openspec/project.md` defines the suite-wide workflow.
- `openspec/specs/<department>/spec.md` records the active contract for each department.
- `openspec/changes/<change-id>/` holds proposal, design, and task files for active work.
- GitHub issues and PRs must name the department and affected event types.

The registry in `src/lemonade_store/departments.py` remains canonical for machine-readable boundaries.

## LLM Wiki Standard

This repo treats Andrej Karpathy's LLM Wiki pattern as the governing source for agent knowledge management: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

For this project, that means:

- `docs/wiki/` is the maintained project memory for architecture, decisions, gotchas, and onboarding.
- `AGENTS.md` is the agent instruction schema.
- `openspec/` is the structured change/spec layer.
- Raw source material stays in docs, examples, tests, issue/PR discussions, and committed specs.
- Agents must update the wiki when they learn durable repo knowledge that future agents need.

Keep wiki entries concise, factual, and linked back to concrete files, specs, or test evidence.

## Wiki Pages

- [[architecture]] — High-level architecture, event envelopes, and configurations.
- [[departments]] — Department event namespace constraints and registry rules.
- [[conventions]] — Python coding style, strict typing, standard library rules, and class design guidelines.
- [[runbook]] — Commands list, Makefile usage, environment variables, and workstation port numbers.
- [[agents]] — Safety policies, owner approval gates, privacy bounds, and prohibited development paths.
