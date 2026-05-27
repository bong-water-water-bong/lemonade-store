# Site Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-site`

## Namespace

`site.*`

## Owns

public website, static pages, product/category pages, soil availability, hours, contact instructions, privacy statement, Cloudflare guide.

## Consumes

marketing.post.approved, marketing.site_update.drafted.

## Emits

site.change.drafted, site.change.approved, site.deploy.requested, site.deploy.completed.

## Owner Approval

deploy, publish_change.

## Must Not

deploy or publish public changes without owner approval.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
