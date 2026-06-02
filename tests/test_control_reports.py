import json
from pathlib import Path

from agent_memory_substrate.control_reports import build_memory_control_report, write_report
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[1]


def _case_by_id(report: dict, case_id: str) -> dict:
    return next(case for case in report["cases"] if case["case_id"] == case_id)


def test_memory_control_report_summarizes_access_boundaries():
    report = build_memory_control_report()

    assert report["artifact_type"] == "memory_control_report"
    assert report["all_passed"] is True
    assert report["case_count"] == 4
    assert report["failed_closed_count"] == 1
    assert report["restricted_leak_count"] == 0
    assert report["blocked_ref_count"] >= 1
    assert report["stale_source_count"] >= 1
    assert report["blocked_reason_counts"]["sensitivity_not_allowed"] >= 1


def test_memory_control_report_preserves_case_level_evidence():
    report = build_memory_control_report()
    semantic = _case_by_id(report, "memory_research_scout_semantic")
    quant = _case_by_id(report, "memory_quant_blocks_restricted")
    stale = _case_by_id(report, "memory_research_scout_stale_episodic")
    unknown = _case_by_id(report, "memory_unknown_role_fail_closed")

    assert "vault-research-001" in semantic["observed"]["retrieved_source_ids"]
    assert "sensitivity_not_allowed" in semantic["observed"]["blocked_reasons"]
    assert semantic["observed"]["restricted_content_leaked"] is False

    assert "idea-sandbox-001" in quant["observed"]["retrieved_source_ids"]
    assert "sensitivity_not_allowed" in quant["observed"]["blocked_reasons"]
    assert quant["observed"]["restricted_content_leaked"] is False

    assert "idea-stale-001" in stale["observed"]["stale_source_ids"]
    assert stale["observed"]["review_required"] is True

    assert unknown["observed"]["status"] == "failed_closed"
    assert unknown["observed"]["retrieved_source_ids"] == []


def test_memory_control_report_validates_against_schema():
    schema = json.loads((ROOT / "schemas" / "memory_control_report.json").read_text())
    validator = Draft7Validator(schema)

    generated_report = build_memory_control_report()
    static_report = json.loads(
        (ROOT / "examples" / "control_reports" / "memory_control_report.json").read_text()
    )

    assert list(validator.iter_errors(generated_report)) == []
    assert list(validator.iter_errors(static_report)) == []


def test_write_report_outputs_memory_control_artifact(tmp_path):
    paths = write_report(tmp_path)
    report_path = paths["memory"]

    assert report_path.name == "memory_control_report.json"
    assert json.loads(report_path.read_text())["all_passed"] is True
