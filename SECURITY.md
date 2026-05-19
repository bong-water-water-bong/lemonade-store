# Security

## Reporting a vulnerability

If you find a security issue in Lemonade Store, please **do not** open
a public issue. Instead, open a GitHub Security Advisory on this repo
(`Security` tab → `Report a vulnerability`) or contact the
maintainers privately.

We aim to acknowledge reports within a week.

## Threat model (v0.1)

Lemonade Store v0.1 is documentation and contracts. There is no
running daemon, no network listener, and no persisted user data in
this repository. The threat surface here is:

- the published Python package (`lemonade-store` on PyPI, if/when
  released), which could be hijacked or tampered with; and
- the docs themselves, which a shop owner may follow verbatim when
  setting up Cloudflare or a public website.

We take both seriously.

## Privacy boundaries inherited from the suite

- No customer card data anywhere.
- No customer audio or images persisted by default.
- No PII leaves the local system unless an owner explicitly approves a
  marketing post or a website change.

## Dependencies

The runtime package has **zero third-party dependencies**. Dev and docs
extras (pytest, ruff, mypy, mkdocs, mkdocs-material) are widely
audited; we pin major versions in `pyproject.toml`.

## Public website

The Cloudflare website is the only public surface in the suite. Form
submissions are protected by Cloudflare Turnstile. The website never
reads the local store database directly — only owner-approved content
crosses the boundary, and it crosses as a commit to the website repo.
