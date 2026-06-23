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

