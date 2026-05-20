# Events — `store.event.v1`

Every Lemonade Store department reads and writes events of shape
`store.event.v1`. The envelope is intentionally small: department
specifics live in `payload`, which is opaque to the envelope
validator.

## Envelope

```json
{
  "schema_version": "store.event.v1",
  "event_id": "evt-0001",
  "ts": "2026-05-19T18:30:00Z",
  "store_id": "tie-dye-farms",
  "department": "cashier",
  "type": "cashier.transaction.closed",
  "source": "lemonade-cashier",
  "actor": { "kind": "attendant", "id": "alice" },
  "requires_approval": false,
  "approved_by": null,
  "payload": { "total": "12.34", "cash_tendered": "15.00", "change": "2.66" }
}
```

## Field rules

| Field | Rule |
| --- | --- |
| `schema_version` | must equal `store.event.v1` |
| `event_id` | required; unique within store_id; deterministic IDs are encouraged |
| `ts` | ISO-8601 UTC timestamp |
| `store_id` | the business identity (e.g. `tie-dye-farms`) |
| `department` | must be a known department (see registry) |
| `type` | must be `namespace.action[.subaction]`; namespace must match the department's namespace, or be a shared meta namespace (`store.*`, `audit.*`) |
| `source` | a human-meaningful producer ID (e.g. `lemonade-cashier`) |
| `actor` | `{ "kind": "attendant" \| "agent_auto" \| "agent_confirmed" \| "supervisor" \| "owner" \| "system", "id": "..." }` |
| `requires_approval` | boolean; gates a public/financial action |
| `approved_by` | string or `null`; must be `null` when `requires_approval` is `false` |
| `payload` | object; department-owned shape |

## Namespace map

| Department | Event namespace |
| --- | --- |
| `cashier` | `cashier.*` |
| `inventory` | `inventory.*` |
| `accounting` | `accounting.*` |
| `marketeer` | `marketing.*` *(differs from department name)* |
| `supplier` | `supplier.*` |
| `reports` | `reports.*` |
| `security` | `security.*` |
| `site` | `site.*` |
| _shared_ | `store.*`, `audit.*` (any department may emit) |

## Approval semantics

- Public side effects (publish a post, deploy the site) must carry
  `requires_approval: true` and remain `approved_by: null` until an
  owner approves them.
- Approval is itself an event (typically `marketing.post.approved` or
  `site.change.approved`) that references the draft `event_id` in its
  payload.
- A consumer that sees `requires_approval: true` and
  `approved_by: null` **must not** take the public action; it may
  surface the draft for review.

## Audit chain

The envelope alone does not hash-chain — that is the cashier's job and
the cashier's `cashier.transaction.*` events carry their own chain.
Cross-department audit links live in `payload.parent_event_id` when
useful. v0.1 does not mandate a global chain; v0.2 may add one if
real-world replay needs it.

## Determinism

`dump_event(event)` produces JSON with `sort_keys=True` so two dumps
of the same logical event are byte-identical. Downstream consumers
that want a SHA-256 fingerprint can hash the line; the same event
will hash the same on any machine.
