# Architecture

> Lemonade Store is the project/spec repo for Lemonade marketplace plugins. It
> defines the shared event envelope and department boundaries, but it is not
> the Lemonade App runtime and it does not launch `lemond`.

## Subprocess Integrations & lemond_process

Although `lemonade-store` is a specs-only repository, the cashier subsystem itself is integrated with an embedded subprocess manager (`lemond_process.py`) running on local port `13400` that handles local LLM-assisted parsing. During environment initialization, `setup_lemond.sh` is executed to pull and configure the necessary embeddable resources (such as offline model files).

## Overview

Lemonade Store is designed as the project/spec home for a family of
single-workstation, local-first Lemonade marketplace plugins. Lemonade App /
Lemonade Server (`lemond`) is the runtime. The department repos — cashier,
accounting, inventory, marketeer, supplier, reports, security, and site — are
plugin source repos. They are packaged separately as Podman plugins and wired
through `lemond`.

This repo acts only as the project contract layer: it publishes the shared
event envelope (`store.event.v1`), the department registry, and store-level
configuration contracts so plugin packages can pin their expectations.

v0.1 ships docs, contracts, and a Tie Dye Farms example config. No agents,
containers, services, or app runtimes are running from this repo.

## How It Works

### Current state (v0.1)

Three small Python modules form the contract package (`src/lemonade_store/`):

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

### Department plugin flow

```
Lemonade App / lemond
  ↕ marketplace/plugin boundary
Podman plugin: cashier
Podman plugin: accounting
Podman plugin: inventory
Podman plugin: supplier
Podman plugin: marketeer
Podman plugin: site
Podman plugin: reports
Podman plugin: security
```

Plugins do not call each other directly. Cross-plugin coordination goes through
`lemond` and approved marketplace/event contracts. No department may rewrite a
closed cashier transaction.

### Example config (Tie Dye Farms)

`examples/tie-dye-farms/` contains `store.toml`, `departments.toml`, `website.toml`, and `sample_events.jsonl`. This is the reference store: a vape/convenience/tobacco/soil shop. The config wires `payment_core = "cash_only"`, `barter = "allowed_with_approval"`, and `cloudflare = "website_only"`.

## Key Decisions

- **Why store is project/spec only:** Lemonade App / `lemond` is the runtime.
  Department repos are marketplace plugin sources. Keeping `lemonade-store` out
  of runtime ownership prevents a department repo from accidentally becoming
  the app.
- **Why every plugin uses Podman:** Plugin isolation must be explicit and
  repeatable. Each department gets its own container, data directory, and
  `LEMOND_BASE_URL`; none of them bind the app port.
- **Why the department registry is a static Python literal, not a runtime config:** Changing the contract is a code review, not an ops action. The static literal is auditable, pinnable, and validated at import time — there is no window between "config loaded" and "contract checked."
- **Why docs-first for v0.1:** Building the shared envelope and department boundaries before any department repo exists prevents the common failure mode where each repo invents its own event schema and the integration layer becomes a translation mess. The envelope is the contract; agreeing on it first means department repos can be written in parallel without coordination debt.
- **Why `marketeer` uses the `marketing` namespace (not `marketeer`):** Event types read naturally in downstream code — `marketing.post.drafted` is unambiguous; `marketeer.post.drafted` is confusing when the consuming repo is named `lemonade-inventory`. The repo name follows the suite convention; the event namespace follows readability.
- **Why zero third-party runtime deps:** The suite must run offline on a single Strix Halo node. Keeping `lemonade_store.*` stdlib-only means it can be vendored into any department repo without a network call or a complex dependency resolver.

## Gotchas

- **v0.1 is contracts-only — no runtime implementation. Don't look for running services.** The `src/` package validates events and loads configs; it does not start any agent, server, container, or background process.
- **Do not start `lemond` from a department repo.** The app owns `13305`.
  Department plugins are Podman packages wired through the marketplace boundary.
- **`marketeer` ≠ `marketing` in event types.** The department name is `marketeer`; its event namespace is `marketing`. If you filter events by namespace prefix, use `marketing.`, not `marketeer.`.
- **Approval state requires checking two fields.** A downstream consumer that only checks `requires_approval` will silently process unapproved draft events. Always check `is_auto()` or (`is_approved()`) before acting on an event with public or financial consequences.
- **`dump_event` produces deterministic JSON, but the envelope does not validate timestamps or UUIDs.** `ts` and `event_id` are free strings at the envelope level. Department repos are responsible for enforcing ISO-8601 timestamps and unique IDs.
- **Changing the envelope schema bumps `SCHEMA_VERSION`.** Old events are not silently re-interpreted. If you add a field to `store.event.v1`, existing JSONL files will not round-trip through the new `load_event` without a migration.

## Related

- [[README]] — wiki entry point and open threads
