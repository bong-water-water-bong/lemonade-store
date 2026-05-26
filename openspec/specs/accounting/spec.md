# Accounting Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-accounting`

## Namespace

`accounting.*`

## Owns

daily close, cash reconciliation, CIT reconciliation, barter ledger, expenses, supplier costs, tax summary exports.

## Consumes

cashier.transaction.closed, cashier.cit.bag.received, cashier.barter.recorded, supplier.order.received, inventory.adjusted.

## Emits

accounting.daily_close, accounting.cash_reconciled, accounting.barter_recorded, accounting.expense_recorded, accounting.export.created.

## Owner Approval

export, tax_filing_summary.

## Must Not

rewrite closed cashier transactions, invent sales, process payments.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
