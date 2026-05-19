# Departments

Each Lemonade Store department lives in its own repo. This document
pins the v0.1 contracts. The canonical machine-readable copy is
`src/lemonade_store/departments.py`; if the two disagree, the Python
file wins.

## Shared shape

Every department declares:

| Field | Meaning |
| --- | --- |
| `name` | identifier (and repo suffix) — e.g. `cashier` |
| `repo` | `lemonade-<name>` |
| `namespace` | event prefix (defaults to `name`; `marketeer` uses `marketing`) |
| `owns` | natural-language list of responsibilities |
| `consumes` | event types this dept reads from the shared log |
| `emits` | event types this dept produces (must be in `namespace.*`) |
| `agents` | agent identifiers this dept runs |
| `requires_owner_approval_for` | action kinds gated by owner approval |
| `reads` | allowed *namespaces* to read from |
| `writes` | allowed *namespaces* to write into (must include only own `namespace.`) |
| `proposals` | proposal types this dept makes to other departments |

## Cashier

- **Repo:** `lemonade-cashier`
- **Namespace:** `cashier.*`
- **Owns:** deterministic checkout, product matching, cart state,
  totals, cash tender, change, receipts, CIT custody, audit/replay,
  attendant-approved barter records.
- **Emits:** `cashier.transaction.opened`,
  `cashier.transaction.line_added`, `cashier.transaction.line_voided`,
  `cashier.transaction.closed`, `cashier.cit.drop`,
  `cashier.cit.pickup`, `cashier.cit.bag.sealed`,
  `cashier.cit.bag.handoff`, `cashier.cit.bag.received`,
  `cashier.barter.recorded`.
- **Must not own:** social posting, website deploys, full accounting
  ledger, card processor integrations.

## Inventory

- **Repo:** `lemonade-inventory`
- **Namespace:** `inventory.*`
- **Owns:** local product catalog, category schema, SKU aliases, stock
  counts, reorder thresholds, soil product records, zone/shelf
  metadata, product images and onboarding metadata.
- **Consumes:** `cashier.transaction.closed`, `supplier.order.received`.
- **Emits:** `inventory.created`, `inventory.adjusted`,
  `inventory.counted`, `inventory.low_stock`,
  `inventory.category.updated`.
- **Owner approval for:** `delete_product`, `rename_category`.

## Accounting

- **Repo:** `lemonade-accounting`
- **Namespace:** `accounting.*`
- **Owns:** daily cash close, cash drawer reconciliation, CIT
  reconciliation, barter ledger, expense records, supplier cost
  records, category and soil sales summaries, tax summary exports, CSV
  exports for the outside accountant.
- **Consumes:** `cashier.transaction.closed`,
  `cashier.cit.bag.received`, `cashier.barter.recorded`,
  `supplier.order.received`, `inventory.adjusted`.
- **Emits:** `accounting.daily_close`, `accounting.cash_reconciled`,
  `accounting.barter_recorded`, `accounting.expense_recorded`,
  `accounting.export.created`.
- **Owner approval for:** `export`, `tax_filing_summary`.
- **Must not:** rewrite closed cashier transactions; invent sales;
  process payments.

## Marketeer

- **Repo:** `lemonade-marketeer`
- **Namespace:** `marketing.*` *(note: different from `name`)*
- **Owns:** organic social post drafts, promotion calendar, product
  copy, website content drafts, campaign ideas, social posting
  checklist.
- **Consumes:** `inventory.created`, `inventory.category.updated`,
  `accounting.daily_close`.
- **Emits:** `marketing.post.drafted`, `marketing.post.approved`,
  `marketing.site_update.drafted`, `marketing.campaign.created`.
- **Owner approval for:** `publish`, `ad_spend`.
- **Must not:** spend ad money by default; publish without approval;
  invent product claims; leak private store data.

## Supplier

- **Repo:** `lemonade-supplier`
- **Namespace:** `supplier.*`
- **Owns:** supplier records, supplier catalog references, purchase
  order drafts, reorder suggestions, received inventory records.
- **Consumes:** `inventory.low_stock`,
  `accounting.expense_recorded`.
- **Emits:** `supplier.po.drafted`, `supplier.order.received`,
  `supplier.price.updated`.
- **Owner approval for:** `po_submit`.

## Reports

- **Repo:** `lemonade-reports`
- **Namespace:** `reports.*`
- **Owns:** end-of-day owner summary, weekly owner digest, slow
  movers, category revenue, cash and CIT exceptions, inventory risk,
  marketing activity summary.
- **Consumes:** `cashier.transaction.closed`,
  `accounting.daily_close`, `inventory.low_stock`,
  `marketing.post.approved`, `supplier.order.received`.
- **Emits:** `reports.daily`, `reports.weekly`, `reports.exception`.

## Site

- **Repo:** `lemonade-site`
- **Namespace:** `site.*`
- **Owns:** public website, static pages, product/category pages, soil
  availability page, store hours, contact instructions, privacy and
  local-data statement, Cloudflare deployment guide.
- **Consumes:** `marketing.post.approved`,
  `marketing.site_update.drafted`.
- **Emits:** `site.change.drafted`, `site.change.approved`,
  `site.deploy.requested`, `site.deploy.completed`.
- **Owner approval for:** `deploy`, `publish_change`.
