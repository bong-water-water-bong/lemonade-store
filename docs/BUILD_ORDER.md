# Build order

A PR that adds a layer to the right of the current frontier should be
rejected unless the frontier is reliably green. This file pins the
frontier.

## v0.1 — contracts (this repo)

- [x] Docs (this repo).
- [x] `store.event.v1` envelope + validation.
- [x] Department registry + validation.
- [x] Tie Dye Farms example (`store.toml`, `departments.toml`,
  `website.toml`, `sample_events.jsonl`).
- [x] Cloudflare website guide.

## reset — marketplace plugin packaging boundary

- [x] Keep `lemonade-store` as project/spec/docs only.
- [x] Create separate `lemonade-marketplace-plugins` workspace.
- [x] Treat every department repo as a plugin source package.
- [x] Require Podman packaging for every plugin.
- [x] Wire plugins through `lemond`, not direct repo integration.
- [ ] Install Podman on the workstation.
- [ ] Build one plugin image per department.
- [ ] Add the marketplace registration bridge expected by `lemond`.

## v0.2 — accounting plugin package

- Add `lemonade-accounting` repo with a single agent (`closer`) that
  reads cashier `events.jsonl` and writes `accounting.daily_close`.
- Define the CSV export shape for the outside accountant.
- Hard timeout on every read; cashier must not be blocked by accounting.

## v0.3 — inventory feed

- Add `lemonade-inventory` repo with a manual catalog and a
  `cashier.transaction.closed` consumer that emits
  `inventory.adjusted`.
- Define soil-specific category fields.

## v0.4 — supplier drafts

- Add `lemonade-supplier` repo with a `buyer` that reacts to
  `inventory.low_stock` with `supplier.po.drafted`. PO submission
  remains owner-gated.

## v0.5 — marketeer drafts

- Add `lemonade-marketeer` repo with a `drafter` that writes
  `marketing.post.drafted`. Publishing is owner-gated.

## v0.6 — site package

- Add `lemonade-site` repo with a `publisher` that translates
  `marketing.post.approved` events into commits on the website repo
  (`tiedye-farms-site`).
- Cloudflare Pages deploy is owner-triggered.

## v0.7 — reports

- Add `lemonade-reports` repo with a `summarizer` that consumes every
  other department and writes `reports.daily` and `reports.weekly`.
- This is last on purpose: reports of nothing are not useful, and
  reports of half a suite are misleading.

## v1.0 — full Tie Dye Farms loop

- Every department green; owner can run a day with one attendant.
- Daily close, owner digest, drafted post, and approved deploy all
  flow through events.

## Out of scope (probably forever)

- Stripe / card readers / wallets / payment gateways in the cashier
  core. These can exist as optional outer integrations later but never
  as required core features.
- Customer card data, audio, or images at rest.
- Cloud-required daily store operation.
