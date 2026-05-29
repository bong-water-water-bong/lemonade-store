# Coding Conventions

> Guidelines for coding style, package design, typing, and dependency management in the `lemonade-store` codebase.

## Python Version & Environment

- **Target Version**: Python 3.11+ is strictly required.
- **Future Imports**: Use `from __future__ import annotations` at the top of all new modules to support forward-declared type hints.
- **Platform Constraints**: Code must run end-to-end on a local workstation environment (optimized for AMD Strix Halo). Avoid assumptions about cloud hosting or network-backed resources during core operations.

## Dependency Management

- **Zero Third-Party Runtime Dependencies**: The core contract package (`src/lemonade_store/`) must rely *only* on the Python standard library. No third-party packages may be imported in `src/`.
- **Developer Extras**: Third-party libraries are limited to development, testing, and documentation extras defined in `pyproject.toml` (e.g., `pytest`, `ruff`, `mypy`, `mkdocs`).

## Code Formatting & Style

- **Linter & Formatter**: We use [Ruff](https://github.com/astral-sh/ruff) for both linting and code formatting.
- **Line Length**: Hard limit of **100 characters** (configured as `line-length = 100` in `pyproject.toml`). An exception is made under Ruff ignore rules for long inline error messages or validation strings (`E501`) to maintain readability.
- **Import Sorting**: Ruff `I` rule is active. Imports must be sorted alphabetically and grouped correctly (standard library, third-party, local package).

## Static Type Checking

- **Strict Type Checking**: [mypy](https://github.com/python/mypy) is used with strict settings (`strict = true` in `pyproject.toml`).
- **Required Annotations**: Every function, method parameter, and return value must be fully type-annotated.
- **No Implicit Optionals**: Use explicit union typing for optional parameters or return values, e.g., `value: str | None = None` instead of letting it be implicit.

## Class Design & Data Models

- **Immutable Dataclasses**: Dataclasses are the preferred container for structured configuration and contracts. Use `@dataclass(frozen=True)` to ensure immutability and thread safety.
- **Post-Init Validation**: Perform schema and value validation inside `__post_init__` to catch configuration bugs at construction time before objects are passed to other departments.

## Error Handling

- **Explicit Failures**: Do not silently swallow exceptions or return generic status values for configuration or validation failures.
- **Custom Exceptions**: Define custom exception classes that inherit from standard built-ins (e.g., `ConfigValidationError(ValueError)`, `DepartmentValidationError(ValueError)`, `EventValidationError(ValueError)`). Raise them early to prevent malformed data from cascading.

## Package Structure & Exports

- **Public API Isolation**: Maintain a clear boundary for the public API by explicitly defining the `__all__` list in `src/lemonade_store/__init__.py`. 
- **Type Information**: Include a `py.typed` marker file in the package root to indicate the package supports inline type annotations.

## OpenSpec and Change Control

Every department-level change must follow the OpenSpec standard before implementation:
- Record new or updated department specifications under `openspec/specs/<department>/spec.md`.
- File a proposal under `openspec/changes/<change-id>/proposal.md` and track execution tasks in `tasks.md`.
- Registry definitions in `src/lemonade_store/departments.py` are the canonical machine-readable boundaries.

## Related

- [[README]] — project wiki entry point
- [[architecture]] — high-level system view and event envelope
- [[departments]] — department registries and boundary constraints
