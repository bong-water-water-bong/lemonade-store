#!/usr/bin/env python3
"""Evaluate a local Lemonade model against Lemonade-owned JSONL datasets.

This is a smoke-test helper, not an agent. It sends synthetic examples to a
local OpenAI-compatible endpoint, asks for compact JSON, and checks whether the
response is parseable and includes the expected top-level fields.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_SERVER_URL = "http://127.0.0.1:13305"
DEFAULT_DATASETS = (
    "cashier_events.jsonl",
    "security_events.jsonl",
    "accounting_events.jsonl",
)


@dataclass(frozen=True)
class DatasetRow:
    id: str
    department: str
    task: str
    input: Any
    expected: dict[str, Any]
    safety: dict[str, Any]
    notes: str


def load_rows(dataset_dir: Path, filenames: list[str] | None = None) -> list[DatasetRow]:
    names = filenames if filenames is not None else list(DEFAULT_DATASETS)
    rows: list[DatasetRow] = []
    for name in names:
        path = dataset_dir / name
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                raise ValueError(f"{path}:{line_number} is blank")
            raw = json.loads(line)
            rows.append(
                DatasetRow(
                    id=raw["id"],
                    department=raw["department"],
                    task=raw["task"],
                    input=raw["input"],
                    expected=raw["expected"],
                    safety=raw["safety"],
                    notes=raw["notes"],
                )
            )
    return rows


_MAX_INPUT_CHARS = 4096


def build_prompt(row: DatasetRow) -> str:
    required_fields = ", ".join(row.expected)
    raw_input = json.dumps(row.input, sort_keys=True)
    # Truncate oversized dataset inputs before they reach the model endpoint.
    if len(raw_input) > _MAX_INPUT_CHARS:
        raw_input = raw_input[:_MAX_INPUT_CHARS] + " [truncated]"
    return (
        f"Department: {row.department}\n"
        f"Task: {row.task}\n"
        f"Input JSON: {raw_input}\n"
        f"Return compact JSON only with these top-level fields: {required_fields}."
    )


def call_model(server_url: str, model: str, row: DatasetRow, timeout: float) -> str:
    url = server_url.rstrip("/") + "/v1/chat/completions"
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are evaluating fit for Lemonade Store. "
                    "Return valid compact JSON only. No markdown. No prose. "
                    "Do not invent card payments, customer audio, or customer images."
                ),
            },
            {"role": "user", "content": build_prompt(row)},
        ],
        "max_tokens": 256,
        "temperature": 0,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"model request failed for {row.id}: {exc}") from exc

    return payload["choices"][0]["message"].get("content", "")


def parse_model_json(content: str) -> Any:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = min((idx for idx in (text.find("{"), text.find("[")) if idx != -1), default=-1)
        end = max(text.rfind("}"), text.rfind("]"))
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def _expected_mismatches(expected: Any, actual: Any, path: str) -> list[str]:
    if isinstance(expected, bool):
        if not isinstance(actual, bool) or actual != expected:
            return [f"{path}: expected {expected!r}, got {actual!r}"]
        return []

    if isinstance(expected, str):
        if not isinstance(actual, str) or actual != expected:
            return [f"{path}: expected {expected!r}, got {actual!r}"]
        return []

    if isinstance(expected, int | float) and not isinstance(expected, bool):
        if not isinstance(actual, int | float) or isinstance(actual, bool) or actual != expected:
            return [f"{path}: expected {expected!r}, got {actual!r}"]
        return []

    if expected is None:
        if actual is not None:
            return [f"{path}: expected null, got {actual!r}"]
        return []

    if isinstance(expected, list):
        if not isinstance(actual, list):
            return [f"{path}: expected list, got {type(actual).__name__}"]
        if len(actual) != len(expected):
            return [f"{path}: expected {len(expected)} items, got {len(actual)}"]
        mismatches: list[str] = []
        for index, (expected_item, actual_item) in enumerate(zip(expected, actual, strict=True)):
            mismatches.extend(_expected_mismatches(expected_item, actual_item, f"{path}[{index}]"))
        return mismatches

    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected object, got {type(actual).__name__}"]
        mismatches = []
        for key, expected_value in expected.items():
            if key not in actual:
                mismatches.append(f"{path}.{key}: missing")
                continue
            mismatches.extend(_expected_mismatches(expected_value, actual[key], f"{path}.{key}"))
        return mismatches

    return [f"{path}: unsupported expected type {type(expected).__name__}"]


def score_row(row: DatasetRow, content: str) -> dict[str, Any]:
    try:
        parsed = parse_model_json(content)
    except json.JSONDecodeError as exc:
        return {
            "id": row.id,
            "department": row.department,
            "valid_json": False,
            "top_level_fields_present": False,
            "passed": False,
            "error": str(exc),
            "raw": content,
        }

    if not isinstance(parsed, dict):
        return {
            "id": row.id,
            "department": row.department,
            "valid_json": True,
            "top_level_fields_present": False,
            "passed": False,
            "error": "model output was not a JSON object",
            "raw": content,
        }

    missing = sorted(set(row.expected) - set(parsed))
    unexpected = sorted(set(parsed) - set(row.expected))
    mismatches = _expected_mismatches(row.expected, parsed, "output")
    return {
        "id": row.id,
        "department": row.department,
        "valid_json": True,
        "top_level_fields_present": not missing,
        "missing_fields": missing,
        "unexpected_fields": unexpected,
        "mismatches": mismatches,
        "passed": not missing and not unexpected and not mismatches,
        "output": parsed,
    }


def run_evaluation(
    dataset_dir: Path,
    model: str,
    server_url: str,
    filenames: list[str] | None,
    limit: int | None,
    timeout: float,
    dry_run: bool,
) -> dict[str, Any]:
    rows = load_rows(dataset_dir, filenames)
    if limit is not None:
        rows = rows[:limit]

    results: list[dict[str, Any]] = []
    for row in rows:
        if dry_run:
            content = json.dumps(row.expected, separators=(",", ":"))
            results.append(score_row(row, content))
        else:
            try:
                content = call_model(server_url, model, row, timeout)
                results.append(score_row(row, content))
            except RuntimeError as exc:
                results.append(
                    {
                        "id": row.id,
                        "department": row.department,
                        "valid_json": False,
                        "top_level_fields_present": False,
                        "passed": False,
                        "error": str(exc),
                    }
                )

    passed = sum(1 for result in results if result["passed"])
    return {
        "model": model,
        "server_url": server_url,
        "dry_run": dry_run,
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Lemonade model id, e.g. Bonsai-8B-gguf")
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL)
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "datasets",
    )
    parser.add_argument(
        "--dataset",
        action="append",
        help="Dataset filename to run. Repeat for more than one. Defaults to all seed files.",
    )
    parser.add_argument("--limit", type=int, help="Run only the first N rows")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Score expected outputs without calling a model. Useful for checking the harness.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    summary = run_evaluation(
        dataset_dir=args.dataset_dir,
        model=args.model,
        server_url=args.server_url,
        filenames=args.dataset,
        limit=args.limit,
        timeout=args.timeout,
        dry_run=args.dry_run,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
