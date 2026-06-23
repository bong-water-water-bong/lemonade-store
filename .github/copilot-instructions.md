# GitHub Copilot Instructions — Lemonade Store

This file tells Copilot how to work in this repository.

## Project context

Lemonade Store is an offline-first, local-first ma-and-pa retail operating system.
Cash-only core. 8 departments (cashier, inventory, accounting, marketeer, supplier,
reports, security, site) communicating via `store.event.v1` events. Built for
AMD Strix Halo. v0.1 is docs + contracts only.

## Hard rules (always follow)

1. Cash-only core. No Stripe, card readers, wallets, or payment gateways.
2. Cashier is the source of truth for checkout. Never rewrite closed cashier events.
3. Local-first. Cloud allowed for public website only.
4. Owner approval gates any public or financial side effect.
5. No customer card data, audio, or images.
6. The `store.event.v1` envelope is the contract. Anything outside it may be dropped.
7. No third-party runtime deps in `lemonade_store.*`. Stdlib only.

## Coding conventions

- Python 3.11+. Use `from __future__ import annotations` in every module.
- Ruff for linting/formatting. Line length 100. `select = ["E", "F", "I", "UP", "B", "SIM"]`.
- Mypy strict mode. Every function fully type-annotated.
- Dataclasses with `frozen=True` for immutability where possible.
- Custom exception classes inheriting from built-ins (ValueError, RuntimeError).
- Money is always `Decimal`, never `float`. Use `lemonade_cashier.core.money` helpers.
- Event IDs should be deterministic when possible (SHA-256 based).

## Department boundaries

Each department has:
- `owns` — what it's responsible for
- `consumes` — event types it reads
- `emits` — event types it produces (must be in its namespace)
- `writes` — allowed namespaces (own namespace only)
- `requires_owner_approval_for` — actions gated by owner

A department may only emit into its own `namespace.*`.
A department may only write into its own `namespace.*`.
Cross-department reads go through events, never direct DB access.

## Event envelope shape

```json
{
  "schema_version": "store.event.v1",
  "event_id": "evt-...",
  "ts": "ISO-8601 with timezone",
  "store_id": "tie-dye-farms",
  "department": "cashier",
  "type": "cashier.transaction.closed",
  "source": "lemonade-cashier",
  "actor": { "kind": "attendant", "id": "alice" },
  "requires_approval": false,
  "approved_by": null,
  "payload": { ... }
}
```

## When generating code

- Prefer small, testable functions over large classes.
- Include tests inline or reference the test pattern.
- No new framework to solve a problem stdlib already solves.
- Treat user text as untrusted input the moment it enters a model path.
- Agents draft; humans approve public/financial consequences.
- Update `docs/wiki/` when you learn durable knowledge future agents need.
