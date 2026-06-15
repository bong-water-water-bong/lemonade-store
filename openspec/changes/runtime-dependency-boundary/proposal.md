# Change Proposal: runtime-dependency-boundary

## Department

- Department: repo
- Repo: lemonade-store
- Namespace: store.*

## Why

`AGENTS.md`, the README, and the wiki state that `lemonade_store.*`
imports standard library only and that the runtime package has no
third-party dependencies. `pyproject.toml` still required
`lemonade-agents`, which pulls GAIA/Torch dependencies into a normal
store install even though this repo is the suite contract/spec package.

## What Changes

- Move `lemonade-agents` from required dependencies to the optional
  `agents` extra.
- Teach the Makefile to create and prefer `.venv` for local development.
- Document the base install versus optional external agent bridge install.

## Affected Events

- Consumes: none
- Emits: none

## Approval Gates

- Owner approval required: no
- Approval type: packaging/docs cleanup; no event contract change

## Boundaries

- Reads: package metadata, README, changelog, wiki
- Writes: package metadata, README, changelog, wiki, OpenSpec change record
- Must not touch: event envelope shape, department registry semantics, example event payloads

## Verification

- [x] `make test`
- [x] `make lint`
- [x] `make type`
- [x] Examples/docs updated if event contracts changed
