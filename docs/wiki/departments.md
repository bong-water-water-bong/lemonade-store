# Department Contracts

> Every lemonade-store department owns one domain, consumes specific events, and emits its own events. This is the contract table.

## Event Envelope
All inter-department messages use `store.event.v1`:
```json
{
  "schema": "store.event.v1",
  "type": "<department>.<event>.<version>",
  "ts": "2026-05-24T17:00:00Z",
  "source": "<repo-name>",
  "payload": { ... }
}
```

## Department Registry

| Department | Repo | Owns | Consumes | Emits |
|-----------|------|------|----------|-------|
| **Cashier** | lemonade-cashier | POS transactions, event log | sensor inputs | `cashier.sale.v1`, `cashier.void.v1`, `cashier.close.v1` |
| **Accounting** | lemonade-accounting | Daily close, reconciliation | `cashier.*` | `accounting.daily_close.v1`, `accounting.discrepancy.v1` |
| **Vision** | lemonade-vision-server | Product scan, image lookup | scan requests | `vision.product_scan.v1`, `vision.deduce_result.v1` |
| **Security** | lemonade-security | Policy audits, AIBOM | all `store.*` | `security.finding.v1`, `security.aibom.v1` |
| **ASR** | lemon-asr | Audio transcription | audio bytes | transcription text (REST, not event) |
| **Mobile** | lemonade-mobile | Flutter client | REST APIs | (not an event emitter — UI only) |

## Adding a New Department
1. Create repo `lemonade-<department>`
2. Add to this table
3. Define event types in `src/lemonade_<department>/events.py`
4. Add to `DEPARTMENTS.md` in this repo with `owns`, `consumes`, `emits` keys
5. Register in `src/lemonade_store/registry.py`

## Cross-Department Rules
- **No direct DB access**: departments communicate only via events, never by querying another department's database
- **Cashier is source of truth**: never modify cashier event log from another department
- **Async by default**: consuming departments process events asynchronously; they must tolerate replay

## Related
- [[README]] — umbrella architecture
- [[architecture]] — high-level system view
