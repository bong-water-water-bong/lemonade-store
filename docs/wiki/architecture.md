# Architecture

> Lemonade Store is the umbrella retail-OS suite that sits above Lemonade Cashier — it defines the shared event envelope and department boundaries that all store-level repos (accounting, inventory, marketeer, supplier, reports, security, site) will consume; in v0.1 only the contracts exist, no agents are implemented.

## Overview

Lemonade Store is designed as a single-workstation, local-first operating system for a ma-and-pa shop. Lemonade Cashier handles checkout and is the sole source of truth for closed transactions. Every other department — accounting, inventory, marketeer, supplier, reports, security, and site — is a separate repo that consumes events the cashier emits. This repo acts as the coordination layer: it publishes the shared event envelope (`store.event.v1`), the department registry, and store-level configuration contracts so all downstream repos can pin their expectations.

v0.1 ships docs, contracts, and a Tie Dye Farms example config. No agents are running. The accounting export from cashier JSONL is planned as the first real cross-department flow.

## How It Works

### Current state (v0.1)

Three small Python modules form the runtime package (`src/lemonade_store/`):

- **`events.py`** — defines the `store.event.v1` envelope (`Event` dataclass, `Actor`, `load_event`, `dump_event`, `EventValidationError`). `dump_event` uses `sort_keys=True` so two serializations of the same event are byte-identical, preserving hash-chain compatibility with cashier's audit log. The `payload` field is intentionally opaque — each department is responsible for its own payload schema.
- **`departments.py`** — a static Python literal registry of all eight departments (`cashier`, `inventory`, `accounting`, `marketeer`, `supplier`, `reports`, `security`, `site`). Each `Department` dataclass records what the repo owns, what events it consumes/emits, which agents it runs, what requires owner approval, and its read/write namespace perimeter. The registry is validated on construction: a department may only emit into its own namespace and write into its own prefix.
- **`config.py`** — a TOML-based store config loader (`StoreConfig`, `load_store_config`, `load_departments_file`). Uses stdlib `tomllib` (Python 3.11+) to enforce the no-third-party-runtime-deps rule. Validates `payment_core` (`cash_only` only), `barter` policy, and `cloudflare` mode at load time.

### The shared event envelope

Every event flowing between departments must conform to `store.event.v1`:

```json
{
  "schema_version": "store.event.v1",
  "event_id": "evt-0001",
  "ts": "2026-05-19T18:30:00Z",
  "store_id": "tie-dye-farms",
  "department": "cashier",
  "type": "cashier.transaction.closed",
  "source": "lemonade-cashier",
  "actor": { "kind": "attendant", "id": "alice" },
  "requires_approval": false,
  "approved_by": null,
  "payload": { "total": "12.34" }
}
```

The `requires_approval` / `approved_by` pair encodes three legal states: **auto** (`false`/`null`), **draft** (`true`/`null`), and **approved** (`true`/`"who"`). The fourth combination (`false`/`"who"`) is invalid and rejected by the validator. Downstream consumers must check both fields before taking a public or financial action.

### Department event flow (planned)

```
cashier  →  accounting (daily close, reconciliation)
cashier  →  inventory (stock depletion)
cashier  →  reports (daily summary)
cashier  →  security (audit)
inventory → supplier (low_stock → po.drafted)
inventory → marketeer (new product copy drafts)
marketeer → site (approved posts → site.change.drafted)
```

Cashier events are the upstream source; all other departments are consumers. No department may rewrite a closed cashier transaction.

### Example config (Tie Dye Farms)

`examples/tie-dye-farms/` contains `store.toml`, `departments.toml`, `website.toml`, and `sample_events.jsonl`. This is the reference store: a vape/convenience/tobacco/soil shop. The config wires `payment_core = "cash_only"`, `barter = "allowed_with_approval"`, and `cloudflare = "website_only"`.

## Key Decisions

- **Why store sits above cashier, not the other way around:** Cashier is operationally critical and must never depend on store-level logic to make a sale. The dependency arrow points inward: cashier emits, everything else consumes. Outages in inventory or accounting cannot block a transaction.
- **Why the department registry is a static Python literal, not a runtime config:** Changing the contract is a code review, not an ops action. The static literal is auditable, pinnable, and validated at import time — there is no window between "config loaded" and "contract checked."
- **Why docs-first for v0.1:** Building the shared envelope and department boundaries before any department repo exists prevents the common failure mode where each repo invents its own event schema and the integration layer becomes a translation mess. The envelope is the contract; agreeing on it first means department repos can be written in parallel without coordination debt.
- **Why `marketeer` uses the `marketing` namespace (not `marketeer`):** Event types read naturally in downstream code — `marketing.post.drafted` is unambiguous; `marketeer.post.drafted` is confusing when the consuming repo is named `lemonade-inventory`. The repo name follows the suite convention; the event namespace follows readability.
- **Why zero third-party runtime deps:** The suite must run offline on a single Strix Halo node. Keeping `lemonade_store.*` stdlib-only means it can be vendored into any department repo without a network call or a complex dependency resolver.

## Gotchas

- **v0.1 is contracts-only — no runtime implementation. Don't look for running services.** The `src/` package validates events and loads configs; it does not start any agent, server, or background process. Each department repo (`lemonade-accounting`, `lemonade-inventory`, etc.) is a separate project that does not yet exist.
- **`marketeer` ≠ `marketing` in event types.** The department name is `marketeer`; its event namespace is `marketing`. If you filter events by namespace prefix, use `marketing.`, not `marketeer.`.
- **Approval state requires checking two fields.** A downstream consumer that only checks `requires_approval` will silently process unapproved draft events. Always check `is_auto()` or (`is_approved()`) before acting on an event with public or financial consequences.
- **`dump_event` produces deterministic JSON, but the envelope does not validate timestamps or UUIDs.** `ts` and `event_id` are free strings at the envelope level. Department repos are responsible for enforcing ISO-8601 timestamps and unique IDs.
- **Changing the envelope schema bumps `SCHEMA_VERSION`.** Old events are not silently re-interpreted. If you add a field to `store.event.v1`, existing JSONL files will not round-trip through the new `load_event` without a migration.

## Related

- [[README]] — wiki entry point and open threads
