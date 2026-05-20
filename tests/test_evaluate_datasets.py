"""Tests for the local dataset evaluation helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

TOOL_PATH = Path(__file__).resolve().parents[1] / "tools" / "evaluate_datasets.py"


def _load_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("evaluate_datasets", TOOL_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_model_json_accepts_plain_and_fenced_json() -> None:
    tool = _load_tool()

    assert tool.parse_model_json('{"cart": []}') == {"cart": []}
    assert tool.parse_model_json('```json\n{"cart": []}\n```') == {"cart": []}


def test_build_prompt_does_not_leak_expected_values() -> None:
    tool = _load_tool()
    row = tool.load_rows(Path(__file__).resolve().parents[1] / "datasets", ["cashier_events.jsonl"])[
        0
    ]

    prompt = tool.build_prompt(row)

    assert "two cokes" in prompt
    assert "cart_delta" in prompt
    assert "Basic correction" not in prompt
    assert "confidence_floor" in prompt


def test_dry_run_scores_all_seed_rows() -> None:
    tool = _load_tool()

    summary = tool.run_evaluation(
        dataset_dir=Path(__file__).resolve().parents[1] / "datasets",
        model="dry-run-model",
        server_url="http://127.0.0.1:13305",
        filenames=None,
        limit=None,
        timeout=1.0,
        dry_run=True,
    )

    assert summary["total"] == 13
    assert summary["passed"] == 13
    assert summary["failed"] == 0


def test_score_row_rejects_wrong_boolean_value() -> None:
    tool = _load_tool()
    row = tool.load_rows(Path(__file__).resolve().parents[1] / "datasets", ["security_events.jsonl"])[
        0
    ]

    result = tool.score_row(
        row,
        '{"findings":[],"block":false,"redact_fields":[],"policy_ids":[]}',
    )

    assert result["passed"] is False
    assert any("output.block" in mismatch for mismatch in result["mismatches"])
