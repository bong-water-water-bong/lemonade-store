# Lemonade Store — Spec

Status: v0.1 (docs + contracts only)
Date: 2026-05-19
Business target: Tie Dye Farms
Hardware target: AMD Strix Halo Linux workstation

## One-line product

Lemonade Store is an offline-first ma-and-pa retail operating system
where each repo acts like a store department and each department owns
agents, permissions, data, and responsibilities.

## Tagline

Offline agents for ma-and-pa retail.

## Business goal

Make a tiny shop run with minimal owner admin work:

- cash-only checkout
- barter records when approved
- cash-in-transit custody
- local inventory
- soil sales tracking
- organic social marketing
- simple accounting
- website publishing through Cloudflare
- owner-readable daily reports

The system must work locally first. Cloud services are allowed for
public website hosting, social posting, or explicit exports, but they
must not be required to complete a sale, close a till, reconcile cash,
or read inventory.

## Umbrella architecture

```text
lemonade-store          suite shell + shared event vocabulary + setup
   ↓
lemonade-cashier        checkout, cash, barter, CIT, receipts (source of truth)
lemonade-inventory      product intake, stock counts, soil/vape/convenience SKUs
lemonade-accounting     ledgers, expenses, tax summaries, cash reconciliation
lemonade-marketeer      product posts, organic campaigns, website copy drafts
lemonade-supplier       purchase orders, supplier comparison, reorder suggestions
lemonade-reports        owner summaries, end-of-day close, weekly snapshots
lemonade-site           static public website, Cloudflare Pages deployment
```

## Core rule

Each repo is a department in the store. Each department defines:

- responsibility
- local data it owns
- events it consumes
- events it emits
- agents it runs
- permissions for each agent
- audit requirements
- owner approval requirements

## Payment boundary

The core store is **cash-only**.

Allowed core path:

- cash
- change
- receipts
- cash-in-transit (CIT)
- barter records when explicitly approved

Not core:

- Stripe
- card readers
- wallets
- payment gateways
- cloud payment processors

Those can be optional outer integrations later. They must never be
required for the cashier to run.

## Barter boundary

Barter is fine, but it must be **explicit**.

Barter must be:

- attendant-approved
- local
- replayable
- auditable
- policy-gated
- visible in reports

Barter must not bypass inventory, tax decisions, audit, or supervisor
policy.

## Local data principles

- SQLite for queryable local records.
- JSONL for append-only events.
- Hash-chain important business events.
- CSV export for outside humans.
- No cloud dependency for daily store operation.
- No customer card data.
- No customer image / audio persistence by default.

## Agent permission model

Every agent declares:

- department
- allowed reads
- allowed writes
- proposal types
- approval requirement
- audit event type

Default rule: **agents draft; humans approve public or financial
consequences.**

## Definition of done for v0.1

- Repo can be cloned and read without extra services.
- Docs explain the suite clearly.
- Department boundaries are explicit.
- Shared event envelope is documented.
- Tie Dye Farms example config exists.
- Cloudflare website setup guide exists.
- Cashier remains the source of truth for checkout.
- No paid cloud service is required.
- No code path claims to process card payments.

## Non-goals for v0.1

- No Stripe.
- No card readers.
- No paid ads automation.
- No automatic public social posting.
- No cloud database.
- No full accounting replacement.
- No autonomous store before cashier is stable.
- No camera implementation inside `lemonade-store`.
