from __future__ import annotations

from pathlib import Path

DOCS = (
    "docs/package-manager/README.md",
    "docs/package-manager/operator-guide.md",
    "docs/package-manager/admin-install-guide.md",
    "docs/package-manager/internal-access.md",
    "docs/package-manager/offline-bundles.md",
    "docs/package-manager/help-center.md",
    "docs/package-manager/departments.md",
    "docs/package-manager/agents.md",
    "docs/package-manager/troubleshooting.md",
    "docs/package-manager/developer-guide.md",
    "docs/package-manager/security-privacy.md",
    "docs/package-manager/admin-repo.md",
    "docs/superpowers/specs/2026-06-25-package-manager-design.md",
)


def test_package_manager_docs_exist_and_are_internal_first():
    root = Path(__file__).resolve().parents[1]
    missing = [doc for doc in DOCS if not (root / doc).exists()]
    assert missing == []

    overview = (root / "docs/package-manager/README.md").read_text(encoding="utf-8")
    assert "internal-only" in overview.lower()
    assert "offline" in overview.lower()
    assert "lemonade-admin" in overview

    developer = (root / "docs/package-manager/developer-guide.md").read_text(encoding="utf-8")
    assert "Developer details are separated" in developer
