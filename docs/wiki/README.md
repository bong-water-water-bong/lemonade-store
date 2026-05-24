# lemonade-store — Wiki

> Umbrella retail-OS suite sitting above lemonade-cashier — store-level orchestration, inventory, and multi-department coordination for a local-first ma-and-pa shop.

## Current State

v0.1 (merged 2026-05-19): docs and contracts only. What exists:

- `src/lemonade_store/` — three stdlib-only Python modules defining the `store.event.v1` envelope, the eight-department registry, and the TOML-based store config loader.
- `docs/` — SPEC, DEPARTMENTS, EVENTS, BUILD_ORDER, DATA_LAYOUT, CLOUDFLARE_WEBSITE, and TIE_DYE_FARMS references.
- `examples/tie-dye-farms/` — a working store config + sample event log (the reference deployment for a vape/convenience/tobacco/soil shop).
- `datasets/` — sample JSONL event logs for cashier, accounting, and security events.

What does not exist yet: any running agent, service, or department repo. The per-department repos (`lemonade-accounting`, `lemonade-inventory`, `lemonade-marketeer`, `lemonade-supplier`, `lemonade-reports`, `lemonade-security`, `lemonade-site`) are planned but not yet created. The next milestone is the accounting export — reading cashier JSONL and emitting `accounting.export.created`.

## Start Here

- [[architecture]] — scope, relationship to cashier, v0.1 contract definitions, event envelope mechanics, department registry design

## Open Threads

- **Accounting export is the frontier.** Per `docs/BUILD_ORDER.md`, the accounting export (reading cashier JSONL, writing `accounting.export.created`) is the first real cross-department flow. Until that lands, no department repo has been exercised against the envelope.
- **Department repos do not exist.** The registry defines eight departments but only `lemonade-cashier` is a real repo. `lemonade-inventory`, `lemonade-accounting`, etc. are placeholders with no code.
- **Vision pipeline integration point is undefined.** The cashier's `sensors.*` stubs exist downstream; how product-image data flows into `inventory.created` events through the vision pipeline has not been specified at the envelope level.

## Article Index

| Article | What it covers |
|---------|----------------|
| [[architecture]] | Scope, cashier relationship, v0.1 contracts, event envelope, department registry, config loader, Tie Dye Farms example |
