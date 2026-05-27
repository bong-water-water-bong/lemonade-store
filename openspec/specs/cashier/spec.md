# Cashier Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-cashier`

## Namespace

`cashier.*`

## Owns

checkout, product matching, cart state, totals, cash tender, change, receipts, CIT custody, audit/replay, approved barter records.

## Consumes

inventory.created, inventory.adjusted, inventory.category.updated.

## Emits

cashier.transaction.opened, cashier.transaction.line_added, cashier.transaction.line_voided, cashier.transaction.closed, cashier.cit.*, cashier.barter.recorded.

## Owner Approval

none for normal checkout; attendant approval for barter records.

## Must Not

social posting, website deploys, accounting ledger ownership, card processor integrations.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
