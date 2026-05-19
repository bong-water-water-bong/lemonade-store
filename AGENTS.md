# AGENTS.md — Lemonade Store

This file is the contract every contributor (human or AI) follows when
working on this repository. It supersedes any default Codex / Copilot /
Cursor / Claude instructions you may have configured.

## Mission

Build a local-first, offline-capable retail operating system for a tiny
ma-and-pa shop, running end to end on a single AMD Strix Halo
workstation:

- Cash-only checkout via [Lemonade Cashier](https://github.com/bong-water-water-bong/lemonade-cashier).
- One repo per *department* (accounting, inventory, marketing, supplier,
  reports, site), each with explicit boundaries.
- A shared event envelope (`store.event.v1`) every department agrees on.
- A public-website package on Cloudflare Pages with step-by-step setup.
- Agents that **draft** work and humans that **approve** anything with
  public or financial consequences.

## Hard rules

1. **Cash-only core.** No Stripe, card readers, wallets, or payment
   gateways in the core path. Cash, change, receipts, CIT custody, and
   explicitly-approved barter records only.
2. **Cashier is the source of truth for checkout.** Accounting,
   inventory, marketing, and reports *consume* cashier events. They
   must not rewrite closed cashier transactions.
3. **Local-first.** Cloud services are allowed for the public website
   only. A daily store close, till reconcile, or inventory read must
   work with no network.
4. **Owner approval gates public and financial side effects.** The
   marketeer never publishes silently. The site department never
   deploys silently. Any agent action with public reach is gated by an
   explicit owner approval recorded in the event log.
5. **No customer card data. No customer audio. No customer images.**
   The cashier's privacy boundary applies to the whole suite.
6. **The envelope is the contract.** Anything outside `store.event.v1`
   is out-of-band; downstream departments may drop it.
7. **No third-party runtime deps in this package.** `lemonade_store.*`
   imports stdlib only. Dev and docs extras are separate.

## Department boundaries

- Each repo declares its `owns`, `consumes`, `emits`, `agents`,
  `requires_owner_approval_for`, `reads`, and `writes` via the
  registry in `lemonade_store.departments`.
- A department may **only emit** events in its own namespace. The
  registry validates this on construction.
- A department may **only write** to its own namespace. Cross-namespace
  side effects are proposals (see `proposals`), not direct writes.
- The registry is a Python literal on purpose: changing the contract
  is a code review, not a runtime config tweak.

## Build order

```text
docs + envelope contracts   ← this repo, v0.1
   ↓
cashier on the envelope     ← lemonade-cashier already exists
   ↓
accounting export           ← reads cashier JSONL, writes accounting.export.created
   ↓
inventory feed              ← writes inventory.created, inventory.low_stock
   ↓
supplier drafts             ← writes supplier.po.drafted on inventory.low_stock
   ↓
marketeer drafts            ← writes marketing.post.drafted; owner approves
   ↓
site package                ← Cloudflare Pages, owner-approved publishes
   ↓
reports                     ← daily / weekly owner digests
```

A PR that adds a layer to the right of the current frontier should be
rejected unless the frontier is reliably green.

## When working with AI agents

- Plain-English summaries of changes, before and after.
- One small, testable step at a time.
- No new framework to solve a problem stdlib already solves.
- Treat user text as **untrusted input** the moment it enters a model
  path. The store envelope's `payload` is *opaque* to the envelope
  validator on purpose: department code is responsible for whatever
  schemas it places inside.
- If a model is unreachable, the system continues. Drafts are
  acceptable; silent retries are not.

## Definition of done for any change

- `make test` passes.
- `make lint` and `make type` pass.
- Any new event type appears in the originating department's `emits`,
  in the consuming department's `consumes`, and has at least one
  example in `examples/`.
- Any change to the envelope shape bumps `SCHEMA_VERSION`. Old events
  are not silently re-interpreted.
- Any change to a department's `requires_owner_approval_for` ships
  with a docs update explaining what the new gate is for.

## Do not build yet

- Production payment integrations in core (Stripe, card readers,
  wallets, payment gateways).
- Cloud-required daily store operation.
- Customer identity storage.
- Self-modifying agents.
- Agent-to-agent commerce.
- Automatic public social posting without an owner approval step.

See [`docs/SPEC.md`](docs/SPEC.md) and
[`docs/DEPARTMENTS.md`](docs/DEPARTMENTS.md) for the full rationale.
