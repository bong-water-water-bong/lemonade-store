"""Store configuration loader.

A store config wires together a business identity, the cashier repo it
points at, currency, and payment/barter policy. v0.1 only knows
`cash_only` for `payment_core`; anything else is a contract bug and is
rejected at load time so a misconfigured store never boots.

Format: TOML. We use `tomllib` from the stdlib (Python >=3.11) so the
core has no third-party dependency. The handoff doc lists `.yaml`
files; we substitute TOML because the suite's hard rule is no
third-party deps in the contracts package.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from lemonade_store.departments import KNOWN_DEPARTMENTS


class ConfigValidationError(ValueError):
    """Raised when a store-config file fails the v0.1 contract."""


_REQUIRED_KEYS: tuple[str, ...] = (
    "store_id",
    "business_name",
    "suite",
    "cashier_repo",
    "website_repo",
    "currency",
    "payment_core",
    "barter",
    "cloudflare",
    "categories",
)

_ALLOWED_PAYMENT_CORE: frozenset[str] = frozenset({"cash_only"})
_ALLOWED_BARTER: frozenset[str] = frozenset({"allowed_with_approval", "not_allowed"})
_ALLOWED_CLOUDFLARE: frozenset[str] = frozenset({"website_only", "off"})


@dataclass(frozen=True)
class StoreConfig:
    store_id: str
    business_name: str
    suite: str
    cashier_repo: str
    website_repo: str
    currency: str
    payment_core: str
    barter: str
    cloudflare: str
    categories: tuple[str, ...] = field(default_factory=tuple)


def load_store_config(path: str | Path) -> StoreConfig:
    """Load and validate a store-config TOML file."""
    data = _read_toml(path)

    missing = [k for k in _REQUIRED_KEYS if k not in data]
    if missing:
        raise ConfigValidationError(
            f"store config {Path(path).name} missing required keys: {missing}"
        )

    payment_core = data["payment_core"]
    if payment_core not in _ALLOWED_PAYMENT_CORE:
        raise ConfigValidationError(
            f"payment_core={payment_core!r} is not allowed in v0.1 "
            f"(allowed: {sorted(_ALLOWED_PAYMENT_CORE)})"
        )

    barter = data["barter"]
    if barter not in _ALLOWED_BARTER:
        raise ConfigValidationError(
            f"barter={barter!r} is not allowed in v0.1 "
            f"(allowed: {sorted(_ALLOWED_BARTER)})"
        )

    cloudflare = data["cloudflare"]
    if cloudflare not in _ALLOWED_CLOUDFLARE:
        raise ConfigValidationError(
            f"cloudflare={cloudflare!r} is not allowed in v0.1 "
            f"(allowed: {sorted(_ALLOWED_CLOUDFLARE)})"
        )

    categories = data["categories"]
    if not isinstance(categories, list) or not all(
        isinstance(c, str) for c in categories
    ):
        raise ConfigValidationError("categories must be a list of strings")

    return StoreConfig(
        store_id=data["store_id"],
        business_name=data["business_name"],
        suite=data["suite"],
        cashier_repo=data["cashier_repo"],
        website_repo=data["website_repo"],
        currency=data["currency"],
        payment_core=payment_core,
        barter=barter,
        cloudflare=cloudflare,
        categories=tuple(categories),
    )


def load_departments_file(path: str | Path) -> tuple[str, ...]:
    """Load a `departments.toml` file and validate every name is known.

    Expected shape:

    ```toml
    departments = ["cashier", "inventory", ...]
    ```
    """
    data = _read_toml(path)
    if "departments" not in data:
        raise ConfigValidationError(
            f"{Path(path).name} must define a `departments` array"
        )
    names = data["departments"]
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise ConfigValidationError("`departments` must be a list of strings")

    unknown = [n for n in names if n not in KNOWN_DEPARTMENTS]
    if unknown:
        raise ConfigValidationError(
            f"unknown departments: {unknown} (known: {sorted(KNOWN_DEPARTMENTS)})"
        )
    return tuple(names)


def _read_toml(path: str | Path) -> dict[str, Any]:
    with open(path, "rb") as f:
        return tomllib.load(f)


def known_departments() -> Iterable[str]:
    """Convenience re-export for callers that don't want to import twice."""
    return sorted(KNOWN_DEPARTMENTS)
