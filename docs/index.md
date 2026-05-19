# Lemonade Store — Documentation

Lemonade Store is the umbrella suite that coordinates store departments
around [Lemonade Cashier](https://github.com/bong-water-water-bong/lemonade-cashier).
This site documents the **contracts** every department repo agrees on.

## Start here

- [Spec](SPEC.md) — the one-page product description and definition of done.
- [Departments](DEPARTMENTS.md) — boundary and event ownership per repo.
- [Events](EVENTS.md) — the `store.event.v1` envelope and namespace rules.
- [Data layout](DATA_LAYOUT.md) — where local data lives.
- [Tie Dye Farms](TIE_DYE_FARMS.md) — the first business and its config.
- [Cloudflare website](CLOUDFLARE_WEBSITE.md) — step-by-step public site setup.
- [Build order](BUILD_ORDER.md) — what to ship next, in what order.

## Hard rules in 30 seconds

1. Cash-only core.
2. Cashier is the source of truth for checkout.
3. Local-first; cloud allowed for website only.
4. Owner approval gates public and financial side effects.
5. No customer card data, audio, or images.
6. Envelope is the contract.
7. No third-party runtime deps in `lemonade_store.*`.

The longer version lives in [`AGENTS.md`](https://github.com/bong-water-water-bong/lemonade-store/blob/main/AGENTS.md).
