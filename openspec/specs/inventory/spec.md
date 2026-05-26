# Inventory Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-inventory`

## Namespace

`inventory.*`

## Owns

product catalog, SKU aliases, stock counts, reorder thresholds, soil product records, zone/shelf metadata.

## Consumes

cashier.transaction.closed, supplier.order.received.

## Emits

inventory.created, inventory.adjusted, inventory.counted, inventory.low_stock, inventory.category.updated.

## Owner Approval

delete_product, rename_category.

## Must Not

rewrite cashier transactions or submit supplier purchase orders directly.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
