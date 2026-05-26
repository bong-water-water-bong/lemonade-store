# Lemonade Store OpenSpec Standard

Status: active
Source of truth: `src/lemonade_store/departments.py`

## Purpose

This folder is the working spec layer for Lemonade Store. It keeps changes organized by department before code is written, reviewed, packaged, or sent to another repo.

## Required Flow

1. Start with a change under `openspec/changes/<change-id>/`.
2. Write `proposal.md` before implementation.
3. Add `design.md` when the change affects event contracts, storage, permissions, packaging, or another department.
4. Break implementation into `tasks.md`.
5. Update the relevant `openspec/specs/<department>/spec.md` when the department contract changes.
6. Run `make test`, `make lint`, and `make type` before marking a change ready.
7. Owner approval is required for public, financial, deployment, export, or publish side effects.

## Departments

- `cashier`
- `inventory`
- `accounting`
- `marketeer`
- `supplier`
- `reports`
- `security`
- `site`

## Hard Boundaries

- `lemonade-store` is the project/spec/contracts repo, not the runtime.
- `lemond` owns app runtime and port `13305`.
- Department repos are plugin source repos.
- Marketplace packaging belongs in `lemonade-marketplace-plugins`.
- Cashier remains source of truth for checkout.
- Agents draft; humans approve public or financial consequences.

## Source Pattern

This OpenSpec standard treats Karpathy's LLM Wiki pattern as the governing source for agent knowledge management: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

- Raw source: repo files, examples, tests, issue/PR context, and department specs.
- Wiki: `docs/wiki/` summarizes durable knowledge for future agents.
- Schema: `AGENTS.md`, GitHub templates, and `openspec/` define how work is proposed, executed, verified, and reviewed.
# OpenSpec Project Standard

Status: active
Source pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## Purpose

This folder is the structured change/spec layer for this repository. It exists so agents and humans agree on intent, design, tasks, and verification before making broad changes.

## Required Flow

1. For non-trivial work, create `openspec/changes/<change-id>/`.
2. Write `proposal.md` first: why, what changes, risk, and verification.
3. Add `design.md` when architecture, storage, permissions, public behavior, or cross-repo contracts change.
4. Track implementation in `tasks.md` and keep task state current.
5. Update `docs/wiki/` with durable architecture, workflow, gotcha, or onboarding knowledge.
6. Verify with this repo's native tests/checks before marking work ready.

## Memory Model

- Raw source: committed files, examples, tests, issues, PRs, and specs.
- Wiki: `docs/wiki/` durable project memory.
- Schema: `AGENTS.md`, GitHub templates, and `openspec/`.

## Guardrails

- Prefer small, reversible changes.
- Do not overwrite existing project-specific rules.
- Do not add speculative frameworks or broad refactors.
- Record assumptions and verification.
