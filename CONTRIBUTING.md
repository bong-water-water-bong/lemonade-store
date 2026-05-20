# Contributing

Thanks for taking a look. Lemonade Store is small on purpose; v0.1 is
docs and contracts only. The bar for contributions is correctness and
clarity, not novelty.

## Ground rules

- Read [`AGENTS.md`](AGENTS.md) first. It pins the rules every change
  has to fit.
- One logical change per PR.
- `make all` must pass (lint, type, test).
- Conventional Commits in the commit message (`feat:`, `fix:`,
  `docs:`, `chore:`, `refactor:`, `test:`, `build:`, `ci:`).
- Branch from `main`; squash-merge; delete the branch on merge.

## Local setup

```sh
git clone https://github.com/bong-water-water-bong/lemonade-store
cd lemonade-store
make install   # installs dev + docs extras
make all
```

Python 3.11+ is required (`tomllib` ships in the stdlib from 3.11).

## Adding an event type

1. Add the event to the originating department's `emits` in
   `src/lemonade_store/departments.py`.
2. Add it to every consuming department's `consumes`.
3. Add an example line to `examples/tie-dye-farms/sample_events.jsonl`.
4. If the event is approval-gated, set `requires_approval: true` in
   the example and document the matching approval event.
5. Update `docs/EVENTS.md` and `docs/DEPARTMENTS.md`.

## Adding a department

Don't, unless the suite genuinely grew. v0.1 has eight departments and
that's enough surface for a ma-and-pa shop. If you are sure:

1. Add it to `KNOWN_DEPARTMENTS`.
2. Add the full `Department(...)` literal in `_DEPARTMENTS`.
3. Update `docs/DEPARTMENTS.md` and `docs/EVENTS.md`.
4. Add a test parametrize entry in `tests/test_departments.py`.

## What not to add

- Card / wallet / processor payment paths.
- A cloud requirement for any non-website flow.
- A framework where stdlib already works.
- An agent that publishes without owner approval.

## Reporting issues

GitHub issues are fine. For anything security-sensitive, see
[`SECURITY.md`](SECURITY.md).
