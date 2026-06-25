"""Build offline ``lemonade-bundle.toml`` manifests from local wheels.

The package manager (`lemonade_store.package_manager`) *consumes* a bundle
manifest. This module *produces* one, so an offline store can actually be
assembled: a maintainer collects the suite wheels into a directory (on a USB
stick or LAN mirror), runs the builder, and gets a hash-verified, optionally
signed manifest the package manager will accept.

Kept stdlib-only to honor the ``lemonade-store`` no-third-party-deps rule.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from lemonade_store.package_manager import (
    MANIFEST_VERSION,
    build_catalog,
    sign_manifest_payload,
)

BOOTSTRAP_DISTRIBUTIONS = {
    "lemonade-store": "store-base",
    "lemonade-admin": "admin",
}


class BundleBuildError(ValueError):
    """Raised when an offline bundle cannot be assembled from local wheels."""


def known_distributions() -> frozenset[str]:
    """Return every distribution name the catalog/bootstrap bundle can include."""
    return frozenset(pkg.distribution for pkg in build_catalog().packages.values()) | frozenset(
        BOOTSTRAP_DISTRIBUTIONS
    )


def _distribution_from_wheel(filename: str) -> str:
    """Map a wheel filename to a distribution name.

    ``lemonade_cashier-0.1.0-py3-none-any.whl`` -> ``lemonade-cashier``.
    """
    stem = filename.split("-")[0]
    return stem.replace("_", "-")


def _version_from_wheel(filename: str) -> str:
    parts = filename.split("-")
    if len(parts) < 2:
        raise BundleBuildError(f"cannot parse version from wheel name {filename!r}")
    return parts[1]


def build_bundle(
    *,
    wheels_dir: str | Path,
    out_path: str | Path,
    suite_version: str,
    source: str,
    signature_key_path: str | Path | None = None,
) -> Path:
    """Assemble ``out_path`` (a manifest) describing wheels in ``wheels_dir``.

    The manifest references each wheel by a path relative to the manifest, with
    a ``sha256:`` digest. When ``signature_key_path`` is given, the manifest is
    signed with the same stdlib HMAC scheme the loader verifies.

    Returns the manifest path.
    """
    wheels_root = Path(wheels_dir)
    out = Path(out_path)
    if not wheels_root.is_dir():
        raise BundleBuildError(f"wheels directory {wheels_root} does not exist")

    wheels = sorted(wheels_root.glob("*.whl"))
    if not wheels:
        raise BundleBuildError(f"no .whl artifacts found in {wheels_root}")

    known = known_distributions()
    rows: list[dict[str, str]] = []
    for wheel in wheels:
        distribution = _distribution_from_wheel(wheel.name)
        if distribution not in known:
            raise BundleBuildError(
                f"{wheel.name} maps to {distribution!r}, which is not a known "
                f"Lemonade distribution (known: {sorted(known)})"
            )
        version = _version_from_wheel(wheel.name)
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        rel = _relative_artifact(out, wheel)
        rows.append(
            {
                "name": _name_for_distribution(distribution),
                "distribution": distribution,
                "version": version,
                "artifact": rel,
                "sha256": f"sha256:{digest}",
            }
        )

    if signature_key_path is None:
        # An unsigned bundle is for development only; the loader still
        # requires a non-empty signature field, so mark it explicitly.
        body = _render_manifest(
            suite_version=suite_version,
            source=source,
            signature="unsigned-dev",
            rows=rows,
        )
    else:
        key = Path(signature_key_path).read_bytes()
        unsigned = _render_manifest(
            suite_version=suite_version,
            source=source,
            signature="",
            rows=rows,
        )
        # Sign exactly what the loader reconstructs: the manifest with an
        # empty signature value, normalized without a trailing newline.
        payload = "\n".join(unsigned.splitlines()).encode()
        signature = sign_manifest_payload(payload, key)
        body = _render_manifest(
            suite_version=suite_version,
            source=source,
            signature=signature,
            rows=rows,
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    return out


def _name_for_distribution(distribution: str) -> str:
    """Return a friendly package name for a distribution.

    Uses the catalog's department/agent name where the distribution maps to a
    single department; otherwise falls back to the distribution name.
    """
    if distribution in BOOTSTRAP_DISTRIBUTIONS:
        return BOOTSTRAP_DISTRIBUTIONS[distribution]
    catalog = build_catalog()
    for pkg in catalog.packages.values():
        if pkg.distribution == distribution and pkg.kind == "department":
            return pkg.name
    return distribution


def _relative_artifact(manifest_path: Path, wheel: Path) -> str:
    manifest_dir = manifest_path.resolve().parent
    wheel_abs = wheel.resolve()
    try:
        return wheel_abs.relative_to(manifest_dir).as_posix()
    except ValueError:
        # Wheel lives outside the manifest dir; use an absolute path.
        return wheel_abs.as_posix()


def _render_manifest(
    *,
    suite_version: str,
    source: str,
    signature: str,
    rows: list[dict[str, str]],
) -> str:
    lines = [
        f'manifest_version = "{MANIFEST_VERSION}"',
        f'suite_version = "{suite_version}"',
        f'source = "{source}"',
        f'signature = "{signature}"',
    ]
    for row in rows:
        lines.append("")
        lines.append("[[packages]]")
        lines.append(f'name = "{row["name"]}"')
        lines.append(f'distribution = "{row["distribution"]}"')
        lines.append(f'version = "{row["version"]}"')
        lines.append(f'artifact = "{row["artifact"]}"')
        lines.append(f'sha256 = "{row["sha256"]}"')
    return "\n".join(lines) + "\n"
