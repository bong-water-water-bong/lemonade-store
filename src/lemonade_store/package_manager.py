"""Offline/internal package manager for the Lemonade Store suite.

The package manager keeps ``lemonade-store`` as the stdlib-only base package
while letting owners/admins choose which department and agent packages to enable
from a USB bundle or LAN mirror manifest. It deliberately rejects public package
URLs because the POS/admin system must remain local-first and internal-only.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from lemonade_store.departments import registry

BASE_DEPARTMENT = "cashier"
AGENTS_DISTRIBUTION = "lemonade-agents"
DEFAULT_PROFILE = "store-operations"
MANIFEST_VERSION = "lemonade.bundle.v1"
STATE_VERSION = "lemonade.install-state.v1"


class CatalogError(ValueError):
    """Raised when a requested package/profile is not in the catalog."""


class ManifestError(ValueError):
    """Raised when an offline bundle manifest is invalid or unsafe."""


class InstallStateError(ValueError):
    """Raised when install state cannot be updated safely."""


@dataclass(frozen=True)
class PackageSpec:
    """Catalog entry for a selectable department or agent."""

    name: str
    kind: str
    distribution: str
    department: str
    agent: str | None = None
    requires: tuple[str, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class ProfileSpec:
    """Recommended package selection profile."""

    name: str
    label: str
    departments: tuple[str, ...]
    agents: tuple[str, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class Catalog:
    """Full selectable package catalog."""

    packages: Mapping[str, PackageSpec]
    profiles: Mapping[str, ProfileSpec]


@dataclass(frozen=True)
class Selection:
    """Dependency-ordered package selection."""

    profile: str | None
    package_names: tuple[str, ...]
    distributions: tuple[str, ...]


@dataclass(frozen=True)
class ManifestPackage:
    """One artifact entry from a local bundle/LAN mirror manifest."""

    name: str
    distribution: str
    version: str
    artifact: str
    sha256: str
    artifact_path: Path


@dataclass(frozen=True)
class BundleManifest:
    """Validated offline bundle manifest."""

    path: Path
    manifest_version: str
    suite_version: str
    source: str
    signature: str
    packages: Mapping[str, ManifestPackage]


@dataclass
class InstalledPackage:
    """Installed package state recorded locally."""

    name: str
    distribution: str
    version: str
    sha256: str
    enabled: bool = True


@dataclass
class InstallState:
    """Local state file for installed/enabled packages."""

    state_version: str = STATE_VERSION
    installed: dict[str, InstalledPackage] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> InstallState:
        state_path = Path(path)
        if not state_path.exists():
            return cls()
        raw = state_path.read_text(encoding="utf-8")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise InstallStateError(f"corrupt install state file {state_path}: {exc}") from exc
        if data.get("state_version") != STATE_VERSION:
            raise InstallStateError(
                f"unsupported install state version {data.get('state_version')!r}"
            )
        installed = {
            name: InstalledPackage(**pkg) for name, pkg in data.get("installed", {}).items()
        }
        return cls(state_version=STATE_VERSION, installed=installed)

    def save(self, path: str | Path) -> None:
        state_path = Path(path)
        state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "state_version": self.state_version,
            "installed": {name: asdict(pkg) for name, pkg in self.installed.items()},
        }
        state_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def record_install(self, name: str, distribution: str, version: str, sha256: str) -> None:
        self.installed[name] = InstalledPackage(
            name=name,
            distribution=distribution,
            version=version,
            sha256=sha256,
            enabled=True,
        )

    def set_enabled(self, name: str, enabled: bool) -> None:
        if name not in self.installed:
            raise InstallStateError(f"package {name!r} is not installed")
        self.installed[name].enabled = enabled


def default_state_path() -> Path:
    """Return the default local install-state path."""
    return Path.home() / ".lemonade" / "package-manager" / "install-state.json"


def build_catalog() -> Catalog:
    """Build the package catalog from the canonical department registry."""
    reg = registry()
    packages: dict[str, PackageSpec] = {}

    for name in _department_order(reg.keys()):
        dept = reg[name]
        packages[name] = PackageSpec(
            name=name,
            kind="department",
            distribution=dept.repo,
            department=name,
            requires=() if name == BASE_DEPARTMENT else (BASE_DEPARTMENT,),
            description=", ".join(dept.owns[:2]),
        )

    for name in _department_order(reg.keys()):
        dept = reg[name]
        for agent in dept.agents:
            if agent in packages:
                raise CatalogError(f"agent name {agent!r} collides with a department name")
            packages[agent] = PackageSpec(
                name=agent,
                kind="agent",
                distribution=AGENTS_DISTRIBUTION,
                department=name,
                agent=agent,
                requires=(name,),
                description=f"{name} agent",
            )

    profiles = {
        "pos-only": ProfileSpec(
            name="pos-only",
            label="POS only",
            departments=("cashier",),
            description="Cashier-only offline point of sale.",
        ),
        DEFAULT_PROFILE: ProfileSpec(
            name=DEFAULT_PROFILE,
            label="Store operations",
            departments=("cashier", "inventory", "accounting", "reports", "security"),
            description="Recommended offline store profile without public marketing/site packages.",
        ),
        "full-suite": ProfileSpec(
            name="full-suite",
            label="Full suite",
            departments=tuple(_department_order(reg.keys())),
            description="All departments, including marketing and optional public-site workflow.",
        ),
        "full-suite-agents": ProfileSpec(
            name="full-suite-agents",
            label="Full suite with agents",
            departments=tuple(_department_order(reg.keys())),
            agents=tuple(sorted(pkg.name for pkg in packages.values() if pkg.kind == "agent")),
            description="All departments and all available agents.",
        ),
    }
    return Catalog(packages=packages, profiles=profiles)


def resolve_selection(
    *,
    profile: str | None = DEFAULT_PROFILE,
    departments: Iterable[str] = (),
    agents: Iterable[str] = (),
    catalog: Catalog | None = None,
) -> Selection:
    """Resolve profile/custom choices into dependency-ordered packages."""
    cat = catalog if catalog is not None else build_catalog()
    requested: list[str] = []
    resolved_profile = profile

    if profile is not None:
        if profile not in cat.profiles:
            raise CatalogError(f"unknown profile {profile!r}")
        profile_spec = cat.profiles[profile]
        requested.extend(profile_spec.departments)
        requested.extend(profile_spec.agents)

    requested.extend(departments)
    requested.extend(agents)

    seen: set[str] = set()
    ordered: list[str] = []

    def visit(name: str) -> None:
        if name in seen:
            return
        if name not in cat.packages:
            raise CatalogError(f"unknown package {name!r}")
        for dep in cat.packages[name].requires:
            visit(dep)
        seen.add(name)
        ordered.append(name)

    visit(BASE_DEPARTMENT)
    for name in requested:
        visit(name)

    distributions = tuple(_dedupe(cat.packages[name].distribution for name in ordered))
    return Selection(
        profile=resolved_profile,
        package_names=tuple(ordered),
        distributions=distributions,
    )


def load_manifest(
    path: str | Path, *, signature_key_path: str | Path | None = None
) -> BundleManifest:
    """Load and validate a local offline/LAN bundle manifest."""
    manifest_path = Path(path)
    data = _read_toml(manifest_path)
    manifest_version = _required_str(data, "manifest_version")
    if manifest_version != MANIFEST_VERSION:
        raise ManifestError(f"unsupported manifest_version {manifest_version!r}")
    suite_version = _required_str(data, "suite_version")
    source = _required_str(data, "source")
    signature = _required_str(data, "signature")
    if signature_key_path is not None:
        _verify_manifest_signature(manifest_path, signature, Path(signature_key_path).read_bytes())
    package_rows = data.get("packages")
    if not isinstance(package_rows, list) or not package_rows:
        raise ManifestError("manifest must contain at least one [[packages]] entry")

    packages: dict[str, ManifestPackage] = {}
    for row in package_rows:
        if not isinstance(row, dict):
            raise ManifestError("each [[packages]] entry must be a table")
        name = _required_str(row, "name")
        distribution = _required_str(row, "distribution")
        version = _required_str(row, "version")
        artifact = _required_str(row, "artifact")
        sha256 = _required_str(row, "sha256")
        artifact_path = _safe_artifact_path(manifest_path.parent, artifact)
        _verify_sha256(artifact_path, sha256)
        packages[distribution] = ManifestPackage(
            name=name,
            distribution=distribution,
            version=version,
            artifact=artifact,
            sha256=sha256,
            artifact_path=artifact_path,
        )

    return BundleManifest(
        path=manifest_path,
        manifest_version=manifest_version,
        suite_version=suite_version,
        source=source,
        signature=signature,
        packages=packages,
    )


def sign_manifest_payload(payload: bytes, key: bytes) -> str:
    """Return an HMAC-SHA256 signature for a manifest payload."""
    return "hmac-sha256:" + hmac.new(key, payload, hashlib.sha256).hexdigest()


def verify_manifest_signature(manifest_path: str | Path, key_path: str | Path) -> str:
    """Return an HMAC-SHA256 manifest signature using a local shared key.

    This stdlib-only verifier gives offline stores a concrete signature
    mechanism without adding cryptography dependencies to ``lemonade-store``.
    Normal bundle manifests store the returned value as ``signature``. A
    future admin package can wrap this with a richer key-management UI.
    """
    return sign_manifest_payload(Path(manifest_path).read_bytes(), Path(key_path).read_bytes())


@dataclass(frozen=True)
class InstallResult:
    """Result from an install operation."""

    package_names: tuple[str, ...]
    distributions: tuple[str, ...]
    state_path: Path


class PackageManager:
    """Install/enable/disable selected packages from a local manifest."""

    def __init__(
        self,
        *,
        state_path: str | Path | None = None,
        runner: Callable[[list[str]], None] | None = None,
    ) -> None:
        self.state_path = Path(state_path) if state_path is not None else default_state_path()
        self._runner = runner if runner is not None else self._run_command

    def install(
        self,
        *,
        manifest_path: str | Path,
        profile: str | None = DEFAULT_PROFILE,
        departments: Iterable[str] = (),
        agents: Iterable[str] = (),
        signature_key_path: str | Path | None = None,
    ) -> InstallResult:
        selection = resolve_selection(profile=profile, departments=departments, agents=agents)
        manifest = load_manifest(manifest_path, signature_key_path=signature_key_path)
        catalog = build_catalog()
        state = InstallState.load(self.state_path)

        for package_name in selection.package_names:
            spec = catalog.packages[package_name]
            artifact = manifest.packages.get(spec.distribution)
            if artifact is None:
                raise ManifestError(
                    f"manifest {manifest.path} does not provide distribution {spec.distribution!r} "
                    f"required by package {package_name!r}"
                )
            self._runner(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--no-index",
                    str(artifact.artifact_path),
                ]
            )
            state.record_install(
                package_name,
                spec.distribution,
                artifact.version,
                artifact.sha256,
            )

        state.save(self.state_path)
        return InstallResult(
            package_names=selection.package_names,
            distributions=selection.distributions,
            state_path=self.state_path,
        )

    def disable(self, name: str) -> None:
        self._set_enabled(name, False)

    def enable(self, name: str) -> None:
        self._set_enabled(name, True)

    def status(self) -> Mapping[str, InstalledPackage]:
        """Return installed package state keyed by package name."""
        return dict(InstallState.load(self.state_path).installed)

    def uninstall_plan(self, name: str) -> tuple[str, ...]:
        """Return the safe uninstall steps for ``name`` without deleting data."""
        state = InstallState.load(self.state_path)
        if name not in state.installed:
            raise InstallStateError(f"package {name!r} is not installed")
        package = state.installed[name]
        return (
            f"disable {name}",
            f"create rollback record for {name}",
            f"remove package code for {package.distribution}",
            f"preserve {name} data directory",
        )

    def _set_enabled(self, name: str, enabled: bool) -> None:
        state = InstallState.load(self.state_path)
        state.set_enabled(name, enabled)
        state.save(self.state_path)

    @staticmethod
    def _run_command(command: list[str]) -> None:
        subprocess.run(command, check=True)


def _department_order(names: Iterable[str]) -> tuple[str, ...]:
    names_set = set(names)
    rest = sorted(name for name in names_set if name != BASE_DEPARTMENT)
    return (BASE_DEPARTMENT, *rest)


def _dedupe(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return tuple(ordered)


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def _required_str(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ManifestError(f"manifest field {key!r} must be a non-empty string")
    return value


def _safe_artifact_path(base: Path, artifact: str) -> Path:
    parsed = urlparse(artifact)
    if parsed.scheme in {"http", "https"}:
        raise ManifestError("public URLs are not allowed in offline package manifests")
    if parsed.scheme and parsed.scheme != "file":
        raise ManifestError(f"unsupported artifact URL scheme {parsed.scheme!r}")
    artifact_path: Path = (
        Path(parsed.path) if parsed.scheme == "file" else (base / artifact).resolve()
    )
    # Guard against directory traversal: the resolved path must be
    # under the base directory (or equal to it).
    try:
        artifact_path.relative_to(base.resolve())
    except ValueError:
        raise ManifestError(f"artifact {artifact!r} resolves outside the base directory") from None
    if not artifact_path.exists():
        raise ManifestError(f"artifact {artifact!r} does not exist at {artifact_path}")
    return artifact_path


def _verify_sha256(path: Path, expected: str) -> None:
    prefix = "sha256:"
    if not expected.startswith(prefix):
        raise ManifestError("sha256 must use the form 'sha256:<hex-digest>'")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    wanted = expected[len(prefix) :]
    if actual != wanted:
        raise ManifestError(
            f"artifact hash mismatch for {path.name}: expected {wanted}, got {actual}"
        )


def _verify_manifest_signature(path: Path, expected: str, key: bytes) -> None:
    if not expected.startswith("hmac-sha256:"):
        raise ManifestError("manifest signature must use the form 'hmac-sha256:<hex-digest>'")
    data = path.read_text(encoding="utf-8")
    unsigned = _replace_signature_value(data, "")
    # Normalize the payload the same way ``build_bundle`` does when
    # signing: strip trailing newline so the hash is deterministic.
    payload = "\n".join(unsigned.splitlines()).encode()
    actual = sign_manifest_payload(payload, key)
    if not hmac.compare_digest(actual, expected):
        raise ManifestError("manifest signature mismatch")


def _replace_signature_value(data: str, value: str) -> str:
    """Replace the top-level ``signature`` value in a TOML manifest.

    Uses a regex anchored at the start of a line to avoid matching
    ``signature`` keys inside nested tables or string values.
    """
    # Match ``signature = "..."`` at the start of a line (top-level only).
    pattern = re.compile(r'^(signature\s*=\s*)"[^"]*"', re.MULTILINE)
    result, count = pattern.subn(rf'\g<1>"{value}"', data, count=1)
    if count == 0:
        raise ManifestError("manifest missing signature field")
    return result
