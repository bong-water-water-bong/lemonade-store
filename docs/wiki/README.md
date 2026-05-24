# Project Wiki: Lemonade Store

## Mission
Build a local-first, offline-capable retail operating system for a tiny ma-and-pa shop, running end-to-end on a single AMD Strix Halo workstation. The system coordinates multiple departments (accounting, inventory, marketing, etc.) around a central cashier.

## Architecture
- **Umbrella Suite**: Coordinates decentralized departments, each living in its own repository.
- **Shared Event Envelope**: All departments communicate via `store.event.v1` JSON events.
- **Local-First / Stdlib-Only**: The runtime package (`lemonade_store.*`) imports only the Python standard library to ensure maximum portability and reliability.
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
