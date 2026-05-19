"""Tests for the shared `store.event.v1` envelope.

The envelope is a contract between every Lemonade Store department repo.
A breaking change here means every downstream department has to update
its consumer code, so we test the envelope's invariants very explicitly.
"""

from __future__ import annotations

import json

import pytest

from lemonade_store.departments import KNOWN_DEPARTMENTS
from lemonade_store.events import (
    SCHEMA_VERSION,
    Actor,
    Event,
    EventValidationError,
    dump_event,
    load_event,
)


def _valid_payload() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "event_id": "evt-0001",
        "ts": "2026-05-19T18:30:00Z",
        "store_id": "tie-dye-farms",
        "department": "cashier",
        "type": "cashier.transaction.closed",
        "source": "lemonade-cashier",
        "actor": {"kind": "attendant", "id": "alice"},
        "requires_approval": False,
        "approved_by": None,
        "payload": {"total": "12.34"},
    }


class TestEventConstruction:
    def test_minimal_event_round_trips(self) -> None:
        original = _valid_payload()
        event = load_event(original)
        restored = json.loads(dump_event(event))
        assert restored == original

    def test_actor_is_typed(self) -> None:
        event = load_event(_valid_payload())
        assert isinstance(event.actor, Actor)
        assert event.actor.kind == "attendant"
        assert event.actor.id == "alice"

    def test_dump_event_is_deterministic_json(self) -> None:
        event = load_event(_valid_payload())
        # Two dumps of the same logical event must be byte-identical so the
        # event log stays diff-friendly and hash-chainable downstream.
        assert dump_event(event) == dump_event(event)


class TestEventRequiredFields:
    @pytest.mark.parametrize(
        "field",
        [
            "schema_version",
            "event_id",
            "ts",
            "store_id",
            "department",
            "type",
            "source",
            "actor",
        ],
    )
    def test_missing_required_field_rejected(self, field: str) -> None:
        payload = _valid_payload()
        del payload[field]
        with pytest.raises(EventValidationError):
            load_event(payload)


class TestEventValueConstraints:
    def test_unknown_schema_version_rejected(self) -> None:
        payload = _valid_payload()
        payload["schema_version"] = "store.event.v999"
        with pytest.raises(EventValidationError):
            load_event(payload)

    def test_unknown_department_rejected(self) -> None:
        payload = _valid_payload()
        payload["department"] = "smokes"
        with pytest.raises(EventValidationError) as exc:
            load_event(payload)
        assert "smokes" in str(exc.value)

    def test_event_type_must_be_namespaced(self) -> None:
        payload = _valid_payload()
        payload["type"] = "transaction_closed"
        with pytest.raises(EventValidationError):
            load_event(payload)

    def test_event_type_namespace_must_match_department_or_be_meta(self) -> None:
        payload = _valid_payload()
        # accounting event masquerading as a cashier event is a contract bug
        payload["department"] = "accounting"
        payload["type"] = "cashier.transaction.closed"
        with pytest.raises(EventValidationError):
            load_event(payload)

    def test_draft_event_is_accepted_with_null_approver(self) -> None:
        # requires_approval=True + approved_by=None is the DRAFT state.
        # Downstream consumers must defer the public action until an
        # approval event arrives; the envelope itself accepts the draft.
        payload = _valid_payload()
        payload["requires_approval"] = True
        payload["approved_by"] = None
        event = load_event(payload)
        assert event.requires_approval is True
        assert event.approved_by is None

    def test_approved_event_is_accepted_with_approver(self) -> None:
        payload = _valid_payload()
        payload["requires_approval"] = True
        payload["approved_by"] = "owner"
        event = load_event(payload)
        assert event.requires_approval is True
        assert event.approved_by == "owner"

    def test_unapproved_event_must_not_carry_approver(self) -> None:
        payload = _valid_payload()
        payload["requires_approval"] = False
        payload["approved_by"] = "owner"
        with pytest.raises(EventValidationError):
            load_event(payload)


class TestEventTypeValidation:
    """Loader fails fast on type violations with `EventValidationError`."""

    @pytest.mark.parametrize(
        "field",
        ["schema_version", "event_id", "ts", "store_id", "department", "type", "source"],
    )
    def test_non_string_scalar_rejected(self, field: str) -> None:
        payload = _valid_payload()
        payload[field] = 42
        with pytest.raises(EventValidationError):
            load_event(payload)

    def test_actor_must_be_mapping(self) -> None:
        payload = _valid_payload()
        payload["actor"] = "alice"
        with pytest.raises(EventValidationError):
            load_event(payload)

    @pytest.mark.parametrize("subfield", ["kind", "id"])
    def test_actor_subfield_must_be_string(self, subfield: str) -> None:
        payload = _valid_payload()
        payload["actor"][subfield] = 7
        with pytest.raises(EventValidationError):
            load_event(payload)

    def test_requires_approval_must_be_boolean(self) -> None:
        payload = _valid_payload()
        payload["requires_approval"] = "yes"
        with pytest.raises(EventValidationError):
            load_event(payload)

    def test_approved_by_must_be_string_or_null(self) -> None:
        payload = _valid_payload()
        payload["requires_approval"] = True
        payload["approved_by"] = 123
        with pytest.raises(EventValidationError):
            load_event(payload)

    @pytest.mark.parametrize("bad_payload", ["not-an-object", 42, ["a", "b"]])
    def test_payload_must_be_object(self, bad_payload: object) -> None:
        payload = _valid_payload()
        payload["payload"] = bad_payload
        with pytest.raises(EventValidationError):
            load_event(payload)


class TestKnownDepartmentsAreReachable:
    @pytest.mark.parametrize("dept", sorted(KNOWN_DEPARTMENTS))
    def test_each_known_department_can_emit_a_v1_event(self, dept: str) -> None:
        from lemonade_store.departments import registry

        namespace = registry()[dept].namespace
        payload = _valid_payload()
        payload["department"] = dept
        payload["type"] = f"{namespace}.heartbeat"
        payload["source"] = f"lemonade-{dept}"
        event = load_event(payload)
        assert event.department == dept


class TestEventClassValidation:
    def test_event_dataclass_validates_on_construct(self) -> None:
        with pytest.raises(EventValidationError):
            Event(
                schema_version=SCHEMA_VERSION,
                event_id="x",
                ts="2026-05-19T18:30:00Z",
                store_id="tie-dye-farms",
                department="not-a-department",
                type="not-a-department.x",
                source="x",
                actor=Actor(kind="attendant", id="alice"),
            )
