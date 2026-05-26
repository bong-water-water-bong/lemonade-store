# Supplier Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-supplier`

## Namespace

`supplier.*`

## Owns

supplier records, catalog references, PO drafts, reorder suggestions, received inventory records.

## Consumes

inventory.low_stock, accounting.expense_recorded.

## Emits

supplier.po.drafted, supplier.order.received, supplier.price.updated.

## Owner Approval

po_submit.

## Must Not

submit purchase orders without owner approval.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
