"""Shape checks for Lemonade-owned model datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATASET_DIR = Path(__file__).resolve().parents[1] / "datasets"
DATASET_FILES = (
    "cashier_events.jsonl",
    "security_events.jsonl",
    "accounting_events.jsonl",
)


def _load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        assert line.strip(), f"{path.name}:{line_number} is blank"
        row = json.loads(line)
        assert isinstance(row, dict), f"{path.name}:{line_number} must be an object"
        rows.append(row)
    return rows


def test_dataset_files_exist_and_are_nonempty() -> None:
    for name in DATASET_FILES:
        path = DATASET_DIR / name
        assert path.exists(), f"missing dataset file {name}"
        assert _load_rows(path), f"{name} must contain at least one row"


def test_dataset_rows_use_expected_local_shape() -> None:
    seen_ids: set[str] = set()

    for name in DATASET_FILES:
        for row in _load_rows(DATASET_DIR / name):
            assert set(row) == {"id", "department", "task", "input", "expected", "safety", "notes"}
            assert row["id"] not in seen_ids
            seen_ids.add(row["id"])
            assert row["department"] in {"cashier", "security", "accounting"}
            assert isinstance(row["task"], str) and row["task"]
            assert isinstance(row["expected"], dict) and row["expected"]
            assert isinstance(row["notes"], str) and row["notes"]

            safety = row["safety"]
            assert safety == {
                "synthetic": True,
                "contains_customer_pii": False,
                "contains_payment_data": safety["contains_payment_data"],
                "requires_human_confirmation": safety["requires_human_confirmation"],
            }
            assert isinstance(safety["contains_payment_data"], bool)
            assert isinstance(safety["requires_human_confirmation"], bool)
