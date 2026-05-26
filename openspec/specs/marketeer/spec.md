# Marketeer Department Spec

Status: active v0.1
Canonical registry: `src/lemonade_store/departments.py`
Department doc: `docs/DEPARTMENTS.md`

## Repo

`lemonade-marketeer`

## Namespace

`marketing.*`

## Owns

organic post drafts, promotion calendar, product copy, website content drafts, campaign ideas.

## Consumes

inventory.created, inventory.category.updated, accounting.daily_close.

## Emits

marketing.post.drafted, marketing.post.approved, marketing.site_update.drafted, marketing.campaign.created.

## Owner Approval

publish, ad_spend.

## Must Not

publish without owner approval, spend ad money by default, invent product claims, leak private store data.

## Change Rules

- Changes to this spec must also update `docs/DEPARTMENTS.md` and `src/lemonade_store/departments.py` when the machine-readable contract changes.
- Event-shape changes must include examples under `examples/`.
- Public, financial, deployment, export, and publish side effects must remain owner-gated.
