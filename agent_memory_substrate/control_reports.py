"""Deterministic access-control reports for the public memory substrate demo."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from agent_memory_substrate.substrate import build_review_packet

DEMO_REVIEWED_AT = "2026-06-02T00:00:00Z"

CONTROL_FIXTURES: list[dict[str, Any]] = [
    {
        "case_id": "memory_research_scout_semantic",
        "role": "research_scout",
        "query": "semantic research ideas with citation freshness",
        "expected_retrieved": ["vault-research-001"],
        "expected_blocked_reason": "sensitivity_not_allowed",
        "expected_review_required": True,
        "expectation": (
            "research scout retrieves allowed semantic context while restricted candidates "
            "remain redacted and trigger review"
        ),
    },
    {
        "case_id": "memory_quant_blocks_restricted",
        "role": "quant_strategy_reviewer",
        "query": "strategy sandbox restricted paper trial",
        "expected_retrieved": ["idea-sandbox-001"],
        "expected_blocked_reason": "sensitivity_not_allowed",
        "expected_review_required": True,
        "expectation": (
            "quant reviewer receives sandbox procedure but restricted strategy memory is redacted"
        ),
    },
    {
        "case_id": "memory_research_scout_stale_episodic",
        "role": "research_scout",
        "query": "older episodic implementation note refresh required",
        "expected_retrieved": ["idea-stale-001"],
        "expected_blocked_reason": None,
        "expected_review_required": True,
        "expectation": "stale episodic memory should be labeled and require review",
    },
    {
        "case_id": "memory_unknown_role_fail_closed",
        "role": "unbounded_agent",
        "query": "read everything",
        "expected_error": "unknown role",
        "expectation": "unknown roles fail closed instead of retrieving context",
    },
]


def _contains_restricted_leak(payload: dict[str, Any]) -> bool:
    serialized = json.dumps(payload, sort_keys=True)
    return (
        "Restricted strategy boundary note" in serialized
        or "Unauthorized roles must never receive this body" in serialized
        or "restricted-strategy-001" in serialized
    )


def review_case(fixture: dict[str, Any]) -> dict[str, Any]:
    role = str(fixture["role"])
    query = str(fixture["query"])
    try:
        packet = build_review_packet(role, query)
    except ValueError as exc:
        error = str(exc)
        checks = {
            "expected_error_present": str(fixture.get("expected_error", "")) in error,
            "retrieval_not_returned": True,
        }
        return {
            "case_id": fixture["case_id"],
            "role": role,
            "query": query,
            "expectation": fixture["expectation"],
            "passed": all(checks.values()),
            "checks": checks,
            "observed": {
                "status": "failed_closed",
                "error": error,
                "retrieved_source_ids": [],
                "blocked_refs": [],
                "blocked_reasons": [],
                "stale_source_ids": [],
                "review_required": True,
                "restricted_content_leaked": False,
                "memory_types_checked": [],
                "source_kinds_checked": [],
            },
        }

    retrieval = packet["retrieval"]
    blocked = retrieval["blocked"]
    telemetry = retrieval["telemetry"]
    blocked_reasons = [hit["reason"] for hit in blocked]
    expected_retrieved = fixture.get("expected_retrieved", [])
    checks = {
        "expected_retrieved_present": all(
            source_id in telemetry["retrieved_source_ids"] for source_id in expected_retrieved
        ),
        "review_required_matches": telemetry["review_required"]
        is fixture["expected_review_required"],
        "restricted_content_redacted": not _contains_restricted_leak(packet),
    }
    expected_blocked_reason = fixture.get("expected_blocked_reason")
    if expected_blocked_reason is not None:
        checks["expected_blocked_reason_present"] = expected_blocked_reason in blocked_reasons
    else:
        checks["no_required_blocked_reason"] = True

    return {
        "case_id": fixture["case_id"],
        "role": role,
        "query": query,
        "expectation": fixture["expectation"],
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "status": "ok",
            "error": None,
            "retrieved_source_ids": telemetry["retrieved_source_ids"],
            "blocked_refs": telemetry["blocked_refs"],
            "blocked_reasons": blocked_reasons,
            "stale_source_ids": packet["stale_source_ids"],
            "review_required": telemetry["review_required"],
            "restricted_content_leaked": _contains_restricted_leak(packet),
            "memory_types_checked": telemetry["memory_types_checked"],
            "source_kinds_checked": telemetry["source_kinds_checked"],
        },
    }


def build_memory_control_report(fixtures: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    selected = fixtures or CONTROL_FIXTURES
    cases = [review_case(fixture) for fixture in selected]
    blocked_reason_counts = Counter(
        reason for case in cases for reason in case["observed"]["blocked_reasons"]
    )
    return {
        "artifact_type": "memory_control_report",
        "reviewed_at": DEMO_REVIEWED_AT,
        "case_count": len(cases),
        "passed_count": sum(1 for case in cases if case["passed"]),
        "failed_count": sum(1 for case in cases if not case["passed"]),
        "all_passed": all(case["passed"] for case in cases),
        "review_required_count": sum(1 for case in cases if case["observed"]["review_required"]),
        "failed_closed_count": sum(
            1 for case in cases if case["observed"]["status"] == "failed_closed"
        ),
        "blocked_ref_count": sum(len(case["observed"]["blocked_refs"]) for case in cases),
        "stale_source_count": sum(len(case["observed"]["stale_source_ids"]) for case in cases),
        "restricted_leak_count": sum(
            1 for case in cases if case["observed"]["restricted_content_leaked"]
        ),
        "blocked_reason_counts": dict(sorted(blocked_reason_counts.items())),
        "cases": cases,
    }


def write_report(out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = build_memory_control_report()
    path = out_dir / "memory_control_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"memory": path}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic memory control report")
    parser.add_argument("--out", type=Path, default=Path("examples") / "control_reports")
    args = parser.parse_args(argv)
    paths = write_report(args.out)
    for name, path in paths.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
