"""The `store.event.v1` envelope.

Every Lemonade Store department repo emits events into a shared JSONL
log. The envelope below is the contract: anything outside it is
out-of-band and a downstream consumer is allowed to drop it.

Design notes worth remembering:

* The envelope is intentionally *small*. Department-specific data lives
  in `payload`, which is opaque here. The envelope only carries enough
  to route, audit, and gate approvals.
* `requires_approval` is paired with `approved_by` because "approved by
  whom" is the audit answer. The two move together, so we reject mixed
  states (approval-required but no approver, or vice versa).
* `dump_event` uses `sort_keys=True` so two dumps of the same logical
  event are byte-identical. Downstream consumers can hash a line and
  expect the same hash on any machine; that keeps the cashier's
  hash-chained audit log property reachable from `lemonade-store`.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from lemonade_store.departments import KNOWN_DEPARTMENTS, registry

SCHEMA_VERSION = "store.event.v1"

# Cross-department namespaces that any department is allowed to emit
# into. `store.*` is for envelope-level meta-events, `audit.*` is for
# cross-cutting audit trail entries. Keep this list short on purpose.
_META_NAMESPACES: frozenset[str] = frozenset({"store", "audit"})

_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "event_id",
    "ts",
    "store_id",
    "department",
    "type",
    "source",
    "actor",
)


class EventValidationError(ValueError):
    """Raised when an event payload fails the v1 envelope contract."""


@dataclass(frozen=True)
class Actor:
    """Who (or what) caused this event.

    `kind` is intentionally a free string today (attendant, agent_auto,
    agent_confirmed, supervisor, owner, system). We expect cashier and
    other departments to enumerate their own allowed kinds; the envelope
    only requires that *something* is recorded.
    """

    kind: str
    id: str


@dataclass
class Event:
    schema_version: str
    event_id: str
    ts: str
    store_id: str
    department: str
    type: str
    source: str
    actor: Actor
    requires_approval: bool = False
    approved_by: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_event(self)


def _namespace_of(event_type: str) -> str:
    head, _, _ = event_type.partition(".")
    return head


def _validate_event(event: Event) -> None:
    if event.schema_version != SCHEMA_VERSION:
        raise EventValidationError(
            f"unknown schema_version {event.schema_version!r}; expected {SCHEMA_VERSION!r}"
        )
    if event.department not in KNOWN_DEPARTMENTS:
        raise EventValidationError(
            f"unknown department {event.department!r}; "
            f"expected one of {sorted(KNOWN_DEPARTMENTS)}"
        )
    if "." not in event.type:
        raise EventValidationError(
            f"event type {event.type!r} is not namespaced (expected 'department.foo.bar')"
        )

    event_ns = _namespace_of(event.type)
    dept_ns = registry()[event.department].namespace
    if event_ns != dept_ns and event_ns not in _META_NAMESPACES:
        raise EventValidationError(
            f"event type {event.type!r} is in namespace {event_ns!r}, "
            f"but department {event.department!r} owns namespace {dept_ns!r}"
        )

    if event.requires_approval and event.approved_by is None:
        raise EventValidationError(
            "requires_approval=True must be paired with a non-null approved_by"
        )
    if not event.requires_approval and event.approved_by is not None:
        raise EventValidationError(
            "approved_by must be null when requires_approval=False"
        )


def load_event(data: Mapping[str, Any]) -> Event:
    """Parse a dict (e.g. from `json.loads`) into a validated `Event`."""
    for required in _REQUIRED_FIELDS:
        if required not in data:
            raise EventValidationError(f"missing required field {required!r}")

    raw_actor = data["actor"]
    if not isinstance(raw_actor, Mapping):
        raise EventValidationError("actor must be an object with 'kind' and 'id'")
    for required in ("kind", "id"):
        if required not in raw_actor:
            raise EventValidationError(f"actor.{required} is required")
    actor = Actor(kind=raw_actor["kind"], id=raw_actor["id"])

    return Event(
        schema_version=data["schema_version"],
        event_id=data["event_id"],
        ts=data["ts"],
        store_id=data["store_id"],
        department=data["department"],
        type=data["type"],
        source=data["source"],
        actor=actor,
        requires_approval=data.get("requires_approval", False),
        approved_by=data.get("approved_by"),
        payload=dict(data.get("payload", {})),
    )


def dump_event(event: Event) -> str:
    """Serialize an `Event` to deterministic JSON.

    `sort_keys=True` and `separators=(",", ":")` aren't used because we
    keep the on-disk form readable — but key ordering is fixed (sorted)
    so two dumps of the same event are byte-identical and downstream
    hash chains stay stable across machines.
    """
    return json.dumps(asdict(event), sort_keys=True, ensure_ascii=False)
