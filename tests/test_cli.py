from __future__ import annotations

from pathlib import Path

from lemonade_store.cli import main
from lemonade_store.package_manager import InstallState


def test_cli_list_shows_profiles_departments_and_agents(capsys):
    code = main(["list"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Profiles:" in out
    assert "store-operations" in out
    assert "Departments:" in out
    assert "inventory: lemonade-inventory" in out
    assert "Agents:" in out
    assert "onboarder: inventory" in out


def test_cli_plan_supports_custom_profile_none(capsys):
    code = main(["plan", "--profile", "none", "--department", "inventory", "--agent", "onboarder"])

    out = capsys.readouterr().out
    assert code == 0
    assert "cashier" in out
    assert "inventory" in out
    assert "onboarder" in out
    assert "lemonade-agents" in out


def test_cli_status_and_uninstall_plan_use_state_file(tmp_path: Path, capsys, monkeypatch):
    state_path = tmp_path / "state.json"
    state = InstallState()
    state.record_install("cashier", "lemonade-cashier", "0.1.0", "sha256:abc")
    state.save(state_path)
    monkeypatch.setenv("LEMONADE_STATE_PATH", str(state_path))

    assert main(["status"]) == 0
    status_out = capsys.readouterr().out
    assert "cashier" in status_out
    assert "enabled" in status_out

    assert main(["uninstall-plan", "cashier"]) == 0
    plan_out = capsys.readouterr().out
    assert "preserve cashier data directory" in plan_out

    code = main(["plan", "--profile", "none", "--department", "badger"])

    captured = capsys.readouterr()
    assert code == 2
    assert "unknown package 'badger'" in captured.err


def test_cli_build_bundle_creates_loadable_manifest(tmp_path: Path, capsys):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    (wheels / "lemonade_cashier-0.1.0-py3-none-any.whl").write_bytes(b"cashier wheel")
    out = tmp_path / "lemonade-bundle.toml"

    code = main(
        [
            "build-bundle",
            "--wheels",
            str(wheels),
            "--out",
            str(out),
            "--suite-version",
            "0.1.0",
            "--source",
            "usb",
        ]
    )

    assert code == 0
    assert out.exists()
    output = capsys.readouterr().out
    assert "lemonade-cashier" in output
