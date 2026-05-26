# Reports Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-reports`

## Namespace

`reports.*`

## Owns

daily summaries, weekly digest, slow movers, category revenue, cash/CIT exceptions, inventory risk, marketing activity summary.

## Consumes

cashier.transaction.closed, accounting.daily_close, inventory.low_stock, marketing.post.approved, supplier.order.received.

## Emits

reports.daily, reports.weekly, reports.exception.

## Owner Approval

none by default; exporting outside local store requires approval through security/store policy.

## Must Not

report on incomplete or unverified data as if final.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
