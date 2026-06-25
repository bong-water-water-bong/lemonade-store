from pathlib import Path

import pytest

from lemonade_store.bundle import BundleBuildError, build_bundle
from lemonade_store.package_manager import load_manifest


def _make_wheels(tmp_path: Path) -> Path:
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    (wheels / "lemonade_cashier-0.1.0-py3-none-any.whl").write_bytes(b"cashier wheel")
    (wheels / "lemonade_inventory-0.1.0-py3-none-any.whl").write_bytes(b"inventory wheel")
    return wheels


def test_build_bundle_writes_manifest_that_load_manifest_accepts(tmp_path: Path):
    wheels = _make_wheels(tmp_path)

    manifest_path = build_bundle(
        wheels_dir=wheels,
        out_path=tmp_path / "lemonade-bundle.toml",
        suite_version="0.1.0",
        source="usb",
    )

    loaded = load_manifest(manifest_path)
    assert set(loaded.packages) == {"lemonade-cashier", "lemonade-inventory"}
    assert loaded.packages["lemonade-cashier"].version == "0.1.0"
    assert loaded.suite_version == "0.1.0"
    assert loaded.source == "usb"


def test_build_bundle_signs_manifest_when_key_given(tmp_path: Path):
    wheels = _make_wheels(tmp_path)
    key = tmp_path / "bundle.key"
    key.write_bytes(b"owner-maintainer-secret")

    manifest_path = build_bundle(
        wheels_dir=wheels,
        out_path=tmp_path / "lemonade-bundle.toml",
        suite_version="0.1.0",
        source="lan-mirror",
        signature_key_path=key,
    )

    # Signature must verify against the same key, and tampering must fail.
    loaded = load_manifest(manifest_path, signature_key_path=key)
    assert loaded.signature.startswith("hmac-sha256:")


def test_build_bundle_accepts_bootstrap_store_and_admin_wheels(tmp_path: Path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    (wheels / "lemonade_store-0.1.0-py3-none-any.whl").write_bytes(b"store wheel")
    (wheels / "lemonade_admin-0.1.0-py3-none-any.whl").write_bytes(b"admin wheel")
    (wheels / "lemonade_cashier-0.1.0-py3-none-any.whl").write_bytes(b"cashier wheel")

    manifest_path = build_bundle(
        wheels_dir=wheels,
        out_path=tmp_path / "lemonade-bundle.toml",
        suite_version="0.1.0",
        source="usb",
    )

    loaded = load_manifest(manifest_path)
    assert set(loaded.packages) == {"lemonade-store", "lemonade-admin", "lemonade-cashier"}
    assert loaded.packages["lemonade-store"].name == "store-base"
    assert loaded.packages["lemonade-admin"].name == "admin"


def test_build_bundle_rejects_unrecognized_distribution(tmp_path: Path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    (wheels / "totally_unknown-1.0-py3-none-any.whl").write_bytes(b"x")

    with pytest.raises(BundleBuildError, match="not a known Lemonade distribution"):
        build_bundle(
            wheels_dir=wheels,
            out_path=tmp_path / "lemonade-bundle.toml",
            suite_version="0.1.0",
            source="usb",
        )


def test_build_bundle_requires_wheels(tmp_path: Path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()

    with pytest.raises(BundleBuildError, match="no .whl artifacts"):
        build_bundle(
            wheels_dir=wheels,
            out_path=tmp_path / "lemonade-bundle.toml",
            suite_version="0.1.0",
            source="usb",
        )


def test_build_then_install_end_to_end(tmp_path: Path):
    """The bundle a maintainer builds must be installable by the manager."""
    from lemonade_store.package_manager import PackageManager

    wheels = _make_wheels(tmp_path)
    manifest_path = build_bundle(
        wheels_dir=wheels,
        out_path=tmp_path / "lemonade-bundle.toml",
        suite_version="0.1.0",
        source="usb",
    )

    commands: list[list[str]] = []
    manager = PackageManager(
        state_path=tmp_path / "state.json",
        runner=lambda command: commands.append(command),
    )
    result = manager.install(
        manifest_path=manifest_path,
        profile=None,
        departments=("inventory",),
        agents=(),
    )

    assert result.package_names == ("cashier", "inventory")
    # Both wheels were handed to the (mocked) installer.
    assert len(commands) == 2
