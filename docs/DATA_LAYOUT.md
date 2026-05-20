# Local data layout

Lemonade Store is local-first. Every department's data lives on the
workstation. v0.1 does not implement the storage; this doc pins the
*shape* downstream repos should target.

## Per-store root

```text
~/lemonade-data/<store_id>/
  store.toml                       # copied from examples/<store_id>/store.toml
  departments.toml
  website.toml
  cashier/
    events.jsonl                   # cashier-owned; hash-chained
    receipts/
    cit/
  inventory/
    products.sqlite                # local catalog, stock, categories
    images/
  accounting/
    ledger.sqlite
    exports/                       # CSVs for the outside accountant
  marketeer/
    drafts/                        # post + site drafts awaiting approval
    calendar.toml
  supplier/
    suppliers.sqlite
    purchase_orders/
  reports/
    daily/
    weekly/
  security/
    findings/
    aibom/
    reports/
  site/
    queue/                         # owner-approved changes waiting to deploy
    drafts/
  store_events.jsonl               # cross-department envelope log (optional)
```

## Rules

1. **Cashier's `events.jsonl` is authoritative.** Other departments may
   *read* it but must never modify it.
2. **SQLite is fine for queryable per-department state.** It is not the
   source of truth — events are.
3. **Department directories never read each other's databases.** Cross
   department reads go through the event log.
4. **Exports are write-only.** Departments may write to
   `<dept>/exports/` for outside humans. They never read each other's
   exports back.
5. **No customer PII at rest.** No card data ever. No customer audio or
   images by default.

## Encryption and backup

v0.1 leaves disk encryption to the OS (LUKS). Backups go to the user's
existing local backup path (a Pi NAS at the time of writing); see the
top-level `~/notes` if you are looking for the exact paths on this
workstation. The store suite itself does not require cloud backup to
function.
