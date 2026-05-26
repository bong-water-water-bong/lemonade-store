# Security Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-security`

## Namespace

`security.*`

## Owns

policy checks, agent audits, AIBOM manifests, model/tool inventory, privacy checks, offline security reports.

## Consumes

cashier.transaction.closed, cashier.cit.bag.received, accounting.daily_close, inventory.created, marketing.post.approved, supplier.order.received, reports.exception, site.deploy.completed.

## Emits

security.finding.created, security.policy.checked, security.aibom.generated, security.audit.completed.

## Owner Approval

export_report, share_finding.

## Must Not

mutate business events or export findings without owner approval.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
