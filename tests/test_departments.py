"""Tests for the department registry contract.

Each Lemonade Store repo is a department. The registry is the single
place that enumerates which departments exist, what they own, what
events they consume/emit, and what they need owner approval for.

Department boundaries are what stops accounting from mutating cashier
events, marketing from spending ad money silently, and inventory from
being rewritten by reports. The tests below pin those boundaries.
"""

from __future__ import annotations

import pytest

from lemonade_store.departments import (
    KNOWN_DEPARTMENTS,
    Department,
    DepartmentValidationError,
    registry,
)

EXPECTED = {
    "cashier",
    "inventory",
    "accounting",
    "marketeer",
    "supplier",
    "reports",
    "site",
}


class TestKnownDepartments:
    def test_known_departments_match_expected(self) -> None:
        assert KNOWN_DEPARTMENTS == EXPECTED

    def test_registry_has_every_known_department(self) -> None:
        for name in EXPECTED:
            assert name in registry()
            assert isinstance(registry()[name], Department)


class TestDepartmentInvariants:
    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_emits_are_namespaced(self, name: str) -> None:
        dept = registry()[name]
        for event_type in dept.emits:
            assert event_type.startswith(f"{dept.namespace}."), (
                f"{name} emits {event_type!r}, which is not in its namespace {dept.namespace!r}"
            )

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_emits_and_consumes_are_disjoint_within_department(self, name: str) -> None:
        dept = registry()[name]
        assert not (set(dept.emits) & set(dept.consumes)), (
            f"{name} both emits and consumes the same event type"
        )

    @pytest.mark.parametrize("name", sorted(EXPECTED))
    def test_department_has_a_repo_and_owns_something(self, name: str) -> None:
        dept = registry()[name]
        assert dept.repo, f"{name} missing repo"
        assert dept.owns, f"{name} owns nothing"


class TestPublicSurfaceRequiresApproval:
    def test_marketeer_publishing_requires_owner_approval(self) -> None:
        marketeer = registry()["marketeer"]
        for needs_approval in ("publish", "ad_spend"):
            assert needs_approval in marketeer.requires_owner_approval_for, (
                f"marketeer must require owner approval for {needs_approval}"
            )

    def test_site_deploy_requires_owner_approval(self) -> None:
        site = registry()["site"]
        assert "deploy" in site.requires_owner_approval_for


class TestCashierIsSourceOfTruth:
    def test_only_cashier_emits_cashier_transactions(self) -> None:
        owner_of_cashier_events = {
            name
            for name, dept in registry().items()
            if any(t.startswith("cashier.transaction.") for t in dept.emits)
        }
        assert owner_of_cashier_events == {"cashier"}

    def test_no_department_other_than_cashier_writes_cashier_events(self) -> None:
        for name, dept in registry().items():
            if name == "cashier":
                continue
            for write in dept.writes:
                assert not write.startswith("cashier."), (
                    f"{name} declares it writes {write!r}; only cashier may"
                )


class TestDepartmentValidation:
    def test_department_cannot_emit_outside_its_namespace(self) -> None:
        with pytest.raises(DepartmentValidationError):
            Department(
                name="accounting",
                repo="lemonade-accounting",
                owns=("ledger",),
                consumes=("cashier.transaction.closed",),
                emits=("cashier.transaction.closed",),  # wrong namespace
                agents=(),
                requires_owner_approval_for=(),
                reads=(),
                writes=(),
            )

    def test_department_cannot_declare_writes_outside_its_namespace(self) -> None:
        with pytest.raises(DepartmentValidationError):
            Department(
                name="reports",
                repo="lemonade-reports",
                owns=("digest",),
                consumes=(),
                emits=("reports.daily",),
                agents=(),
                requires_owner_approval_for=(),
                reads=(),
                writes=("cashier.transaction.closed",),  # not allowed
            )
