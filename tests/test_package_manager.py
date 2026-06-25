from pathlib import Path

import pytest

from lemonade_store.package_manager import (
    CatalogError,
    InstallState,
    ManifestError,
    PackageManager,
    build_catalog,
    load_manifest,
    resolve_selection,
    sign_manifest_payload,
)


def test_catalog_contains_departments_agents_and_profiles():
    catalog = build_catalog()

    assert catalog.packages["cashier"].kind == "department"
    assert catalog.packages["cashier"].distribution == "lemonade-cashier"
    assert catalog.packages["inventory"].requires == ("cashier",)
    assert catalog.packages["onboarder"].kind == "agent"
    assert catalog.packages["onboarder"].distribution == "lemonade-agents"
    assert catalog.packages["onboarder"].requires == ("inventory",)
    assert catalog.profiles["store-operations"].departments == (
        "cashier",
        "inventory",
        "accounting",
        "reports",
        "security",
    )


def test_resolve_selection_defaults_to_store_operations_and_orders_dependencies():
    selection = resolve_selection(profile="store-operations", departments=(), agents=("onboarder",))

    assert selection.profile == "store-operations"
    assert selection.package_names == (
        "cashier",
        "inventory",
        "accounting",
        "reports",
        "security",
        "onboarder",
    )
    assert selection.distributions == (
        "lemonade-cashier",
        "lemonade-inventory",
        "lemonade-accounting",
        "lemonade-reports",
        "lemonade-security",
        "lemonade-agents",
    )


def test_resolve_selection_rejects_unknown_package():
    with pytest.raises(CatalogError, match="unknown package 'badger'"):
        resolve_selection(profile=None, departments=("badger",), agents=())


def test_manifest_verifies_hashes_and_rejects_public_urls(tmp_path: Path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    artifact = wheels / "lemonade_cashier-0.1.0-py3-none-any.whl"
    artifact.write_bytes(b"cashier wheel")
    digest = "sha256:7f92ba8732dd8730d3e488a875300df5a3f9a52e5a8f7b5fa89803d95a7552ba"
    manifest = tmp_path / "lemonade-bundle.toml"
    manifest.write_text(
        f'''
manifest_version = "lemonade.bundle.v1"
suite_version = "0.1.0"
source = "usb"
signature = "dev-placeholder"

[[packages]]
name = "cashier"
distribution = "lemonade-cashier"
version = "0.1.0"
artifact = "wheels/lemonade_cashier-0.1.0-py3-none-any.whl"
sha256 = "{digest}"
'''.strip(),
        encoding="utf-8",
    )

    loaded = load_manifest(manifest)

    assert loaded.packages["lemonade-cashier"].artifact_path == artifact

    manifest.write_text(
        manifest.read_text(encoding="utf-8")
        + '\n\n[[packages]]\nname = "bad"\ndistribution = "bad"\nversion = "1"\nartifact = "https://example.com/bad.whl"\nsha256 = "sha256:00"\n',
        encoding="utf-8",
    )
    with pytest.raises(ManifestError, match="public URLs are not allowed"):
        load_manifest(manifest)


def test_manifest_signature_can_be_verified_with_local_key(tmp_path: Path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    artifact = wheels / "lemonade_cashier-0.1.0-py3-none-any.whl"
    artifact.write_bytes(b"cashier wheel")
    unsigned_body = """
manifest_version = "lemonade.bundle.v1"
suite_version = "0.1.0"
source = "usb"
signature = ""

[[packages]]
name = "cashier"
distribution = "lemonade-cashier"
version = "0.1.0"
artifact = "wheels/lemonade_cashier-0.1.0-py3-none-any.whl"
sha256 = "sha256:7f92ba8732dd8730d3e488a875300df5a3f9a52e5a8f7b5fa89803d95a7552ba"
""".strip()
    key = tmp_path / "bundle.key"
    key.write_bytes(b"owner-maintainer-secret")
    signature = sign_manifest_payload(unsigned_body.encode(), key.read_bytes())
    manifest = tmp_path / "lemonade-bundle.toml"
    manifest.write_text(
        unsigned_body.replace('signature = ""', f'signature = "{signature}"'),
        encoding="utf-8",
    )

    loaded = load_manifest(manifest, signature_key_path=key)

    assert loaded.signature == signature

    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace(signature, "hmac-sha256:bad"),
        encoding="utf-8",
    )
    with pytest.raises(ManifestError, match="manifest signature mismatch"):
        load_manifest(manifest, signature_key_path=key)


def test_package_manager_plans_installs_and_records_state(tmp_path: Path):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    cashier = wheels / "lemonade_cashier-0.1.0-py3-none-any.whl"
    cashier.write_bytes(b"cashier wheel")
    inventory = wheels / "lemonade_inventory-0.1.0-py3-none-any.whl"
    inventory.write_bytes(b"inventory wheel")
    manifest = tmp_path / "lemonade-bundle.toml"
    manifest.write_text(
        """
manifest_version = "lemonade.bundle.v1"
suite_version = "0.1.0"
source = "usb"
signature = "dev-placeholder"

[[packages]]
name = "cashier"
distribution = "lemonade-cashier"
version = "0.1.0"
artifact = "wheels/lemonade_cashier-0.1.0-py3-none-any.whl"
sha256 = "sha256:7f92ba8732dd8730d3e488a875300df5a3f9a52e5a8f7b5fa89803d95a7552ba"

[[packages]]
name = "inventory"
distribution = "lemonade-inventory"
version = "0.1.0"
artifact = "wheels/lemonade_inventory-0.1.0-py3-none-any.whl"
sha256 = "sha256:be4699dd42726d35eab517beffe712558209e9036d5e77edf862d2fb44ed902e"
""".strip(),
        encoding="utf-8",
    )
    commands: list[list[str]] = []

    def runner(command: list[str]) -> None:
        commands.append(command)

    state_path = tmp_path / "state.json"
    manager = PackageManager(state_path=state_path, runner=runner)

    result = manager.install(
        profile=None, departments=("inventory",), agents=(), manifest_path=manifest
    )

    assert result.package_names == ("cashier", "inventory")
    assert [cmd[-1] for cmd in commands] == [str(cashier), str(inventory)]
    state = InstallState.load(state_path)
    assert state.installed["cashier"].enabled is True
    assert state.installed["inventory"].version == "0.1.0"


def test_package_manager_install_verifies_signature_key_when_provided(tmp_path: Path):
    from lemonade_store.bundle import build_bundle

    wheels = tmp_path / "wheels"
    wheels.mkdir()
    (wheels / "lemonade_cashier-0.1.0-py3-none-any.whl").write_bytes(b"cashier wheel")
    key = tmp_path / "bundle.key"
    key.write_bytes(b"owner-maintainer-secret")
    wrong_key = tmp_path / "wrong.key"
    wrong_key.write_bytes(b"wrong-secret")
    manifest = build_bundle(
        wheels_dir=wheels,
        out_path=tmp_path / "lemonade-bundle.toml",
        suite_version="0.1.0",
        source="usb",
        signature_key_path=key,
    )
    manager = PackageManager(state_path=tmp_path / "state.json", runner=lambda command: None)

    with pytest.raises(ManifestError, match="manifest signature mismatch"):
        manager.install(
            manifest_path=manifest,
            profile=None,
            departments=("cashier",),
            agents=(),
            signature_key_path=wrong_key,
        )

    result = manager.install(
        manifest_path=manifest,
        profile=None,
        departments=("cashier",),
        agents=(),
        signature_key_path=key,
    )

    assert result.package_names == ("cashier",)


def test_status_lists_installed_packages_and_safe_uninstall_plan(tmp_path: Path):
    state_path = tmp_path / "state.json"
    state = InstallState()
    state.record_install("cashier", "lemonade-cashier", "0.1.0", "sha256:abc")
    state.record_install("inventory", "lemonade-inventory", "0.1.0", "sha256:def")
    state.set_enabled("inventory", False)
    state.save(state_path)
    manager = PackageManager(state_path=state_path, runner=lambda command: None)

    status = manager.status()
    plan = manager.uninstall_plan("inventory")

    assert status["cashier"].enabled is True
    assert status["inventory"].enabled is False
    assert plan == (
        "disable inventory",
        "create rollback record for inventory",
        "remove package code for lemonade-inventory",
        "preserve inventory data directory",
    )

    state_path = tmp_path / "state.json"
    state = InstallState()
    state.record_install("cashier", "lemonade-cashier", "0.1.0", "sha256:abc")
    state.save(state_path)
    manager = PackageManager(state_path=state_path, runner=lambda command: None)

    manager.disable("cashier")
    assert InstallState.load(state_path).installed["cashier"].enabled is False

    manager.enable("cashier")
    assert InstallState.load(state_path).installed["cashier"].enabled is True
