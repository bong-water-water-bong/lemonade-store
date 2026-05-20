# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `security` as a Lemonade Store department contract for
  `lemonade-security`, covering local policy checks, agent audits,
  AIBOM manifests, privacy findings, and the Lemonade SDK security
  plugin boundary.

## [0.1.0] — 2026-05-19

### Added

- Initial scaffold: docs + contracts only, no agents.
- `store.event.v1` envelope with validation
  (`lemonade_store.events.load_event` / `dump_event`).
- Department registry with seven departments
  (`cashier`, `inventory`, `accounting`, `marketeer`, `supplier`,
  `reports`, `site`) and per-department validation of emit / write
  namespaces.
- `StoreConfig` loader from TOML, with refusal to guess currency or
  payment-core mode.
- Tie Dye Farms example: `store.toml`, `departments.toml`,
  `website.toml`, `sample_events.jsonl`.
- Cloudflare Pages public-website setup guide.
- Cashier-grade hygiene: `Makefile`, `pyproject.toml` (ruff + mypy
  strict), GitHub Actions CI, mkdocs site, `CODEOWNERS`,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.

[Unreleased]: https://github.com/bong-water-water-bong/lemonade-store/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bong-water-water-bong/lemonade-store/releases/tag/v0.1.0
