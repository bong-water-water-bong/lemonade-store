# Lemonade-Owned Model Datasets

These JSONL files are local, synthetic training and evaluation examples for
Lemonade Store models. They are deliberately small at first so the examples stay
easy to inspect by a shop owner.

## Rules

- Use Lemonade-authored examples only.
- Do not copy public Hugging Face retail datasets into this folder.
- Do not include real customer audio, real customer images, real card data, real
  tokens, real passwords, phone numbers, addresses, or real receipts.
  Exception: security/policy datasets may contain *synthetic* prohibited-shaped
  placeholders (e.g. `"customer_audio": "synthetic_placeholder"`) specifically
  to test that the model flags, redacts, or blocks them. Such rows must set
  `synthetic: true` and the expected output must block or redact the field.
- Keep money math deterministic in code. Model examples may parse intent, but
  Python/SQLite code must calculate totals, tax, change, and export policy.
- Mark uncertain product matches with confirmation requirements.
- Use one JSON object per line.

## Shared Fields

Each row uses this shape:

```json
{
  "id": "cashier-0001",
  "department": "cashier",
  "task": "parse_cashier_event",
  "input": "two cokes, remove one, add milk",
  "expected": {},
  "safety": {
    "synthetic": true,
    "contains_customer_pii": false,
    "contains_payment_data": false,
    "requires_human_confirmation": false
  },
  "notes": "Short explanation for humans reviewing the example."
}
```

The `expected` object is department-owned. It should be strict enough for model
smoke tests, but not a replacement for department business logic.

## Local Evaluation

With a local Lemonade server running, test a model against the seed rows:

```sh
python3 tools/evaluate_datasets.py --model Bonsai-8B-gguf
```

To check the harness without calling a model:

```sh
python3 tools/evaluate_datasets.py --model dry-run --dry-run
```

## Files

- `cashier_events.jsonl` teaches parsing, cart intent, quantity adjustment, and
  low-confidence product handling.
- `security_events.jsonl` teaches local policy classification and blocking
  unsafe payloads before data leaves the workstation.
- `accounting_events.jsonl` teaches accounting intent and export gating, while
  leaving arithmetic to deterministic code.
