# Tie Dye Farms

The first Lemonade Store business. The configuration below mirrors
`examples/tie-dye-farms/`.

## Identity

| Field | Value |
| --- | --- |
| `store_id` | `tie-dye-farms` |
| `business_name` | Tie Dye Farms |
| `suite` | `lemonade-store` |
| `cashier_repo` | `lemonade-cashier` |
| `website_repo` | `tiedye-farms-site` |
| `currency` | `USD` *(configurable)* |
| `payment_core` | `cash_only` |
| `barter` | `allowed_with_approval` |
| `cloudflare` | `website_only` |

## Categories

- vape
- convenience
- soil
- tobacco

The **soil** category is first-class because Tie Dye Farms also plans
to operate a soil warehouse. Soil-specific reports and inventory
behavior should not be retrofits to "general convenience SKUs"; they
get their own category from day one.

## Departments enabled

All eight: cashier, inventory, accounting, marketeer, supplier,
reports, security, site.

## Website plan

- Domain: TBD (set in `examples/tie-dye-farms/website.toml`).
- Static site, deployed via Cloudflare Pages from `tiedye-farms-site`.
- Pages: home, products, soil, hours-location, contact, privacy,
  promotions.
- Turnstile on the contact form.

## Operating expectations

- A single attendant at the till most days.
- Cash drawer reconciliation at every shift change.
- CIT bag pickup on the existing cashier schedule.
- Daily close fires an `accounting.daily_close` event.
- Owner reviews drafted social posts once a day; approvals are events.
- No card readers. No cloud-required workflow except the website
  publish step.

## What the agents will do (later)

- **Inventory onboarder:** scan the soil shelf, propose
  `inventory.created` and `inventory.adjusted` events.
- **Accounting closer:** at 22:00 each day, summarize the day's cashier
  events and write `accounting.daily_close`.
- **Marketing drafter:** suggest organic Instagram posts about new soil
  stock; owner approves with one tap.
- **Supplier buyer:** when `inventory.low_stock` fires, draft a
  `supplier.po.drafted` event referencing the existing supplier.
- **Reports summarizer:** end-of-day owner digest with sales, CIT
  exceptions, and pending approvals.
- **Security auditor:** local-only checks for agent permissions,
  privacy boundaries, AIBOM completeness, and policy drift.

v0.1 of this repo does **not** implement any of those agents. It pins
the contracts they will share.
