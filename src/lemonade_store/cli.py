"""Command-line interface for the offline Lemonade package manager."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from lemonade_store.package_manager import (
    DEFAULT_PROFILE,
    CatalogError,
    ManifestError,
    PackageManager,
    build_catalog,
    resolve_selection,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``lemonade`` CLI."""
    parser = argparse.ArgumentParser(
        prog="lemonade",
        description="Offline/internal package manager for Lemonade Store.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List profiles, departments, and agents")
    list_parser.add_argument(
        "--kind",
        choices=("all", "profiles", "departments", "agents"),
        default="all",
        help="Filter the list output.",
    )

    plan_parser = subparsers.add_parser("plan", help="Show what would be installed")
    _add_selection_args(plan_parser)

    install_parser = subparsers.add_parser("install", help="Install from a USB bundle/LAN mirror")
    _add_selection_args(install_parser)
    install_parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Path to lemonade-bundle.toml in the local bundle or LAN mirror.",
    )

    disable_parser = subparsers.add_parser("disable", help="Disable an installed package")
    disable_parser.add_argument("name")

    enable_parser = subparsers.add_parser("enable", help="Re-enable an installed package")
    enable_parser.add_argument("name")

    subparsers.add_parser("status", help="Show installed package state")

    uninstall_plan_parser = subparsers.add_parser(
        "uninstall-plan", help="Show safe uninstall steps without deleting data"
    )
    uninstall_plan_parser.add_argument("name")

    args = parser.parse_args(argv)
    if hasattr(args, "profile"):
        args.profile = _normalize_profile(args.profile)

    try:
        if args.command == "list":
            print(_format_catalog(args.kind))
            return 0
        if args.command == "plan":
            selection = resolve_selection(
                profile=args.profile,
                departments=args.department,
                agents=args.agent,
            )
            print(_format_selection(selection.package_names, selection.distributions))
            return 0
        if args.command == "install":
            manager = _manager()
            result = manager.install(
                manifest_path=args.manifest,
                profile=args.profile,
                departments=args.department,
                agents=args.agent,
            )
            print(_format_selection(result.package_names, result.distributions))
            print(f"state: {result.state_path}")
            return 0
        if args.command == "disable":
            _manager().disable(args.name)
            print(f"disabled: {args.name}")
            return 0
        if args.command == "enable":
            _manager().enable(args.name)
            print(f"enabled: {args.name}")
            return 0
        if args.command == "status":
            status = _manager().status()
            if not status:
                print("No packages installed.")
                return 0
            for package in status.values():
                enabled = "enabled" if package.enabled else "disabled"
                print(f"{package.name}: {package.distribution} {package.version} {enabled}")
            return 0
        if args.command == "uninstall-plan":
            for step in _manager().uninstall_plan(args.name):
                print(step)
            return 0
    except (CatalogError, ManifestError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"error: unsupported command {args.command!r}", file=sys.stderr)
    return 2


def _manager() -> PackageManager:
    state_path = os.environ.get("LEMONADE_STATE_PATH")
    if state_path:
        return PackageManager(state_path=state_path)
    return PackageManager()


def _add_selection_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help="Install profile to start from; use 'none' for custom-only.",
    )
    parser.add_argument(
        "--department",
        action="append",
        default=[],
        help="Department package to include. Can be repeated.",
    )
    parser.add_argument(
        "--agent",
        action="append",
        default=[],
        help="Agent to include. Can be repeated.",
    )


def _normalize_profile(value: str | None) -> str | None:
    if value in {None, "none", "custom"}:
        return None
    return value


def _format_catalog(kind: str) -> str:
    catalog = build_catalog()
    lines: list[str] = []
    if kind in {"all", "profiles"}:
        lines.append("Profiles:")
        for profile in catalog.profiles.values():
            lines.append(f"  {profile.name}: {profile.label} — {profile.description}")
    if kind in {"all", "departments"}:
        lines.append("Departments:")
        for pkg in catalog.packages.values():
            if pkg.kind == "department":
                lines.append(f"  {pkg.name}: {pkg.distribution}")
    if kind in {"all", "agents"}:
        lines.append("Agents:")
        for pkg in sorted(catalog.packages.values(), key=lambda p: p.name):
            if pkg.kind == "agent":
                lines.append(f"  {pkg.name}: {pkg.department} ({pkg.distribution})")
    return "\n".join(lines)


def _format_selection(package_names: Sequence[str], distributions: Sequence[str]) -> str:
    return "\n".join(
        (
            "Packages:",
            *(f"  {name}" for name in package_names),
            "Distributions:",
            *(f"  {dist}" for dist in distributions),
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
