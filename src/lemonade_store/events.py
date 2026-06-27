"""The `store.event.v1` envelope.

Every Lemonade Store department repo emits events into a shared JSONL
log. The envelope below is the contract: anything outside it is
out-of-band and a downstream consumer is allowed to drop it.

Design notes worth remembering:

* The envelope is intentionally *small*. Department-specific data lives
  in `payload`, which is opaque here. The envelope only carries enough
  to route, audit, and gate approvals.
* `requires_approval` and `approved_by` together encode three states:
  auto (`False`/`None`), draft (`True`/`None`), and approved
  (`True`/`"who"`). Only the fourth combination — `False`/`"who"`,
  pre-approval of an action that didn't need it — is invalid. See
  `_validate_event` for the rationale.
* `dump_event` uses `sort_keys=True` so two dumps of the same logical
  event are byte-identical. Downstream consumers can hash a line and
  expect the same hash on any machine; that keeps the cashier's
  hash-chained audit log property reachable from `lemonade-store`.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from lemonade_store.departments import KNOWN_DEPARTMENTS, registry

SCHEMA_VERSION = "store.event.v1"

# Cross-department namespaces that any department is allowed to emit
# into. `store.*` is for envelope-level meta-events, `audit.*` is for
# cross-cutting audit trail entries. Keep this list short on purpose.
_META_NAMESPACES: frozenset[str] = frozenset({"store", "audit"})

# ISO-8601 with optional fractional seconds and mandatory timezone.
# Accepts Z, ±HH:MM, or ±HHMM offsets. Constrained to UTC-aware
# timestamps only (no naive datetimes cross the envelope).
# Timezone hour is validated to 00-23 (offsets beyond ±23:59 are
# invalid in practice even if ISO-8601 theoretically allows up to
# ±25:59 for historical leap-seconds).
_ISO8601_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?"
    r"(Z|[+-](?:0[0-9]|1[0-9]|2[0-3]):[0-5]\d|[+-](?:0[0-9]|1[0-9]|2[0-3])[0-5]\d)$"
)

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


@dataclass(frozen=True)
class Event:
    schema_version: str
    event_id: str
    ts: str
    store_id: str
    department: str
    type: str
    source: str
    actor: Actor = field(compare=False)
    requires_approval: bool = False
    approved_by: str | None = None
    payload: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        _validate_event(self)

    def is_auto(self) -> bool:
        """True when this event does not require approval (normal automatic event)."""
        return not self.requires_approval

    def is_draft(self) -> bool:
        """True when this event is awaiting approval (requires_approval=True, not yet approved)."""
        return self.requires_approval and self.approved_by is None

    def is_approved(self) -> bool:
        """True when this event has been explicitly approved."""
        return self.requires_approval and self.approved_by is not None


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
            f"unknown department {event.department!r}; expected one of {sorted(KNOWN_DEPARTMENTS)}"
        )
    if "." not in event.type:
        raise EventValidationError(
            f"event type {event.type!r} is not namespaced (expected 'department.foo.bar')"
        )

    # Validate the timestamp is ISO-8601 with timezone.
    # The envelope contract requires UTC-aware timestamps; naive
    # datetimes or unparseable strings are rejected at the boundary.
    if not _ISO8601_RE.match(event.ts):
        raise EventValidationError(
            f"ts={event.ts!r} must be ISO-8601 with timezone offset "
            f"(e.g. '2026-05-19T18:30:00Z' or '2026-05-19T18:30:00+00:00')"
        )
    try:
        parsed = datetime.fromisoformat(event.ts.replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise EventValidationError(
            f"ts={event.ts!r} is not a valid ISO-8601 datetime: {exc}"
        ) from exc
    if parsed.tzinfo is None:
        raise EventValidationError(
            f"ts={event.ts!r} must include a timezone offset (e.g. 'Z', '+00:00', or '-05:00')"
        )

    event_ns = _namespace_of(event.type)
    dept = registry()[event.department]
    dept_ns = dept.namespace
    if event_ns != dept_ns and event_ns not in _META_NAMESPACES:
        raise EventValidationError(
            f"event type {event.type!r} is in namespace {event_ns!r}, "
            f"but department {event.department!r} owns namespace {dept_ns!r}"
        )

    # Validate that the specific event type is declared in the
    # department's `emits` tuple. A department cannot emit an event
    # type it never declared — this closes the gap between "namespace
    # matches" and "event type is registered."
    if event.type not in dept.emits:
        raise EventValidationError(
            f"event type {event.type!r} is not in the emit list of "
            f"department {event.department!r} (declared emits: {sorted(dept.emits)})"
        )

    # Approval pair semantics:
    #
    #   requires_approval=False, approved_by=None     → normal automatic event
    #   requires_approval=True,  approved_by=None     → DRAFT awaiting approval
    #   requires_approval=True,  approved_by="alice"  → APPROVED action
    #   requires_approval=False, approved_by="alice"  → invalid (you can't
    #                                                   pre-approve an action
    #                                                   that doesn't need
    #                                                   approval)
    #
    # The DRAFT state is the whole reason `requires_approval` exists in the
    # envelope: downstream consumers must check BOTH fields and only take a
    # public/financial action on events that are either auto OR approved.
    if not event.requires_approval and event.approved_by is not None:
        raise EventValidationError("approved_by must be null when requires_approval=False")


def load_event(data: Mapping[str, Any]) -> Event:
    """Parse a dict (e.g. from `json.loads`) into a validated `Event`.

    Every field is type-checked before construction so a malformed JSON
    payload always raises `EventValidationError` (not `TypeError` /
    `KeyError`) — downstream consumers can rely on a single exception
    type when defending the envelope.
    """
    for required in _REQUIRED_FIELDS:
        if required not in data:
            raise EventValidationError(f"missing required field {required!r}")

    for scalar in (
        "schema_version",
        "event_id",
        "ts",
        "store_id",
        "department",
        "type",
        "source",
    ):
        if not isinstance(data[scalar], str):
            raise EventValidationError(
                f"{scalar} must be a string, got {type(data[scalar]).__name__}"
            )

    raw_actor = data["actor"]
    if not isinstance(raw_actor, Mapping):
        raise EventValidationError("actor must be an object with 'kind' and 'id'")
    for required in ("kind", "id"):
        if required not in raw_actor:
            raise EventValidationError(f"actor.{required} is required")
        if not isinstance(raw_actor[required], str):
            raise EventValidationError(
                f"actor.{required} must be a string, got {type(raw_actor[required]).__name__}"
            )
    actor = Actor(kind=raw_actor["kind"], id=raw_actor["id"])

    requires_approval = data.get("requires_approval", False)
    if not isinstance(requires_approval, bool):
        raise EventValidationError(
            f"requires_approval must be a boolean, got {type(requires_approval).__name__}"
        )

    approved_by = data.get("approved_by")
    if approved_by is not None and not isinstance(approved_by, str):
        raise EventValidationError(
            f"approved_by must be a string or null, got {type(approved_by).__name__}"
        )

    raw_payload = data.get("payload", {})
    if not isinstance(raw_payload, Mapping):
        raise EventValidationError(f"payload must be an object, got {type(raw_payload).__name__}")

    return Event(
        schema_version=data["schema_version"],
        event_id=data["event_id"],
        ts=data["ts"],
        store_id=data["store_id"],
        department=data["department"],
        type=data["type"],
        source=data["source"],
        actor=actor,
        requires_approval=requires_approval,
        approved_by=approved_by,
        payload=dict(raw_payload),
    )


def dump_event(event: Event) -> str:
    """Serialize an `Event` to deterministic JSON.

    `sort_keys=True` and `separators=(",", ":")` aren't used because we
    keep the on-disk form readable — but key ordering is fixed (sorted)
    so two dumps of the same event are byte-identical and downstream
    hash chains stay stable across machines.
    """
    return json.dumps(asdict(event), sort_keys=True, ensure_ascii=False)
