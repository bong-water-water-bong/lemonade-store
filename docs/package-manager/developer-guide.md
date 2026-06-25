# Developer Guide

Developer details are separated from operator/admin docs. This section is for maintainers adding package-manager features, departments, agents, or release tooling.

## Core dependency rule

`lemonade-store` must remain stdlib-only at runtime. Do not add third-party runtime dependencies to implement the package-manager engine.

## Adding a department

1. Add the department to `src/lemonade_store/departments.py`.
2. Add tests for registry validation and package catalog resolution.
3. Ensure the package has a local artifact in bundle manifests.
4. Document owner approval gates and data boundaries.

## Adding an agent

1. Add the agent to the owning department registry entry.
2. Add a catalog test proving the agent requires its department.
3. Add Help Center docs explaining what the agent can and cannot do.

## Release process

1. Build wheels for selected repos in a clean environment.
2. Compute `sha256:<digest>` for each artifact.
3. Write `lemonade-bundle.toml`.
4. Sign the manifest with the store-maintainer key workflow.
5. Verify with `lemonade plan` and a test install on a disposable local environment.

## Future work

- Real uninstall/rollback implementation with environment snapshots.
- Strong asymmetric signatures if the project chooses a dependency-bearing admin package for key management.
- Per-department environments or containers behind the same package-manager interface.
