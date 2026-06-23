# Department Contracts

> Every lemonade-store department owns one domain, consumes specific events,
> and emits its own events. This is the live contract table matching
> `src/lemonade_store/departments.py`.

## Event Envelope

All inter-department messages use `store.event.v1`:

```json
{
  "schema_version": "store.event.v1",
  "event_id": "evt-0001",
  "ts": "2026-05-24T17:00:00Z",
  "store_id": "tie-dye-farms",
  "department": "cashier",
  "type": "cashier.transaction.closed",
  "source": "lemonade-cashier",
  "actor": { "kind": "attendant", "id": "alice" },
  "requires_approval": false,
  "approved_by": null,
  "payload": { ... }
}
```

## Department Registry (v0.1)

| Department | Repo | Namespace | Owns | Consumes | Emits |
|---|---|---|---|---|---|
| **cashier** | lemonade-cashier | `cashier.*` | checkout, cash, CIT, receipts, audit/replay | `inventory.*` | `cashier.transaction.*`, `cashier.cit.*`, `cashier.barter.recorded` |
| **inventory** | lemonade-inventory | `inventory.*` | product catalog, SKU aliases, stock counts, soil | `cashier.transaction.closed`, `supplier.order.received` | `inventory.created`, `inventory.adjusted`, `inventory.counted`, `inventory.low_stock`, `inventory.category.updated` |
| **accounting** | lemonade-accounting | `accounting.*` | daily close, cash/CIT reconciliation, barter ledger, tax exports | `cashier.*`, `supplier.order.received`, `inventory.adjusted` | `accounting.daily_close`, `accounting.cash_reconciled`, `accounting.barter_recorded`, `accounting.expense_recorded`, `accounting.export.created` |
| **marketeer** | lemonade-marketeer | `marketing.*` | social post drafts, promotion calendar, website copy | `inventory.*`, `accounting.daily_close` | `marketing.post.drafted`, `marketing.post.approved`, `marketing.site_update.drafted`, `marketing.campaign.created` |
| **supplier** | lemonade-supplier | `supplier.*` | supplier catalog, purchase orders, reorder suggestions | `inventory.low_stock`, `accounting.expense_recorded` | `supplier.po.drafted`, `supplier.order.received`, `supplier.price.updated` |
| **reports** | lemonade-reports | `reports.*` | end-of-day summaries, weekly digest, exceptions | `cashier.transaction.closed`, `accounting.daily_close`, `inventory.low_stock`, `marketing.post.approved`, `supplier.order.received` | `reports.daily`, `reports.weekly`, `reports.exception` |
| **security** | lemonade-security | `security.*` | policy checks, agent audits, AIBOM manifests, privacy findings | all departments (read-only) | `security.finding.created`, `security.policy.checked`, `security.aibom.generated`, `security.audit.completed` |
| **site** | lemonade-site | `site.*` | public website, Cloudflare Pages deploy | `marketing.post.approved`, `marketing.site_update.drafted` | `site.change.drafted`, `site.change.approved`, `site.deploy.requested`, `site.deploy.completed` |

> **Note:** marketeer's event namespace is `marketing.*` (not `marketeer.*`) so
> event types read naturally — e.g. `marketing.post.drafted`.

## Adding a New Department

1. Create repo `lemonade-<department>`
2. Add `Department(...)` entry to `src/lemonade_store/departments.py`
3. Add the department name to `KNOWN_DEPARTMENTS` in the same file
4. Update `docs/DEPARTMENTS.md` with `owns`, `consumes`, `emits` keys
5. Add a spec under `openspec/specs/<department>/spec.md`
6. Update this wiki page

The canonical registry is `src/lemonade_store/departments.py` — if this
wiki and the Python file disagree, the Python file wins.

## Cross-Department Rules

- **No direct DB access**: departments communicate only via events, never by querying another department's database
- **Cashier is source of truth**: never modify cashier event log from another department
- **Async by default**: consuming departments process events asynchronously; they must tolerate replay
- **Namespace perimeter**: a department may only write into its own `namespace.*` prefix
- **Owner approval gates**: any public or financial side effect must carry `requires_approval: true` and be explicitly approved

## Related

- [[README]] — umbrella architecture
- [[architecture]] — high-level system view
- `src/lemonade_store/departments.py` — canonical machine-readable registry
- `docs/DEPARTMENTS.md` — full department contract documentation
