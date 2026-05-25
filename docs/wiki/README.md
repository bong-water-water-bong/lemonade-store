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
- **No Runtime Dependencies**: Do not add third-party dependencies to the runtime package.
- **No App Runtime Here**: Do not launch `lemond`, bind `13305`, or add app
  service/container files to this repo. Plugin packaging belongs in
  `lemonade-marketplace-plugins`.
