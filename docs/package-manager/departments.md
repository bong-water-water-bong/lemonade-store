# Department Packages

The package manager derives department choices from `src/lemonade_store/departments.py`.

## Default store operations departments

- `cashier`: checkout source of truth.
- `inventory`: products, stock, categories, images.
- `accounting`: daily close, cash reconciliation, CSV exports.
- `reports`: owner summaries and exception reports.
- `security`: local policy checks, audits, privacy findings.

## Optional departments

- `supplier`: supplier records, purchase orders, received inventory.
- `marketeer`: drafts for organic marketing and site copy.
- `site`: optional public website workflow, disabled by default.

## Dependency rule

Every non-cashier department depends on cashier because cashier is the source of truth for checkout events.
