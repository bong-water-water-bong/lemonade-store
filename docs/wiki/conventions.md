# Conventions

This document outlines the coding standards, repository guidelines, and architectural conventions for the Lemonade Store system.

## Hard Architectural Rules

1. **Cash-Only Core**: Explicitly forbids Stripe, credit card readers, or other third-party payment gateways in the core checkout path.
2. **Local-First & Offline-Capable**: Daily store closes, till reconciliations, and transactional audits must work offline without any cloud dependencies.
3. **No Third-Party Runtime Dependencies**: Core code under `src/lemonade_store/` must only import Python standard library modules to ensure maximum portability.
4. **Untrusted Input handling**: Any user-supplied text entering a parsing path (such as transcription inputs) is treated as untrusted to prevent injection attacks.
5. **No Customer PII / Persistence**: Persisting or processing customer images, audio bytes, or credit card details is prohibited.

## OpenSpec and Change Control

Every department-level change must follow the OpenSpec standard before implementation:
- Record new or updated department specifications under `openspec/specs/<department>/spec.md`.
- File a proposal under `openspec/changes/<change-id>/proposal.md` and track execution tasks in `tasks.md`.
- Registry definitions in `src/lemonade_store/departments.py` are the canonical machine-readable boundaries.
