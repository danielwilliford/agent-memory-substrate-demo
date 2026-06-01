import json
import subprocess
import sys
from typing import get_args

import pytest
from agent_memory_substrate import build_demo_substrate, build_review_packet, retrieve_for_role
from agent_memory_substrate.models import MEMORY_TYPE_SOURCE_KINDS, MemoryType
from agent_memory_substrate.scoring import deterministic_similarity


def test_research_scout_retrieves_public_semantic_memory():
    packet = retrieve_for_role("research_scout", "semantic research ideas with citation freshness")
    ids = packet.telemetry["retrieved_source_ids"]
    assert "vault-research-001" in ids
    assert packet.telemetry["memory_types_checked"] == [
        "episodic",
        "procedural",
        "semantic",
        "working",
    ]
    assert all("Restricted synthetic content" not in hit.content for hit in packet.hits)


def test_quant_reviewer_gets_allowed_context_and_blocks_restricted_strategy():
    packet = retrieve_for_role("quant_strategy_reviewer", "strategy sandbox restricted paper trial")
    retrieved = set(packet.telemetry["retrieved_source_ids"])
    blocked = set(packet.telemetry["blocked_source_ids"])
    assert "idea-sandbox-001" in retrieved
    assert "restricted-strategy-001" in blocked
    assert all(hit.source_id != "restricted-strategy-001" for hit in packet.hits)


def test_blocked_context_trace_does_not_leak_body():
    review = build_review_packet("quant_strategy_reviewer", "restricted strategy note")
    blocked = review["retrieval"]["blocked"]
    assert {
        "source_id": "restricted-strategy-001",
        "reason": "sensitivity_not_allowed",
    } in blocked
    serialized = json.dumps(review)
    assert "Restricted strategy boundary note" not in serialized
    assert "Unauthorized roles must never receive this body" not in serialized
    assert all("title" not in blocked_hit for blocked_hit in blocked)


def test_stale_episodic_source_label_appears_in_review_packet():
    review = build_review_packet(
        "research_scout", "older episodic implementation note refresh required"
    )
    assert "idea-stale-001" in review["stale_source_ids"]
    assert review["retrieval"]["telemetry"]["review_required"] is True


def test_unknown_role_fails_closed():
    with pytest.raises(ValueError):
        retrieve_for_role("unbounded_agent", "read everything")


def test_demo_command_outputs_harness_adapter_packet():
    result = subprocess.run(
        [sys.executable, "-m", "agent_memory_substrate.demo"],
        check=True,
        text=True,
        capture_output=True,
    )
    packet = json.loads(result.stdout)
    assert packet["mode"] == "harness_agnostic_memory_substrate"
    assert packet["adapter_shape"]["telemetry"]["role"] == "quant_strategy_reviewer"
    assert packet["human_decision_boundary"].endswith("human approval.")


def test_similarity_is_deterministic_and_dependency_light():
    first = deterministic_similarity(
        "semantic retrieval",
        "semantic retrieval over notes",
        ["semantic retrieval"],
    )
    second = deterministic_similarity(
        "semantic retrieval",
        "semantic retrieval over notes",
        ["semantic retrieval"],
    )
    assert first == second
    assert first > 0


def test_blocked_context_is_filtered_before_content_scoring():
    review = build_review_packet("quant_strategy_reviewer", "Unauthorized roles")
    serialized = json.dumps(review)
    assert "restricted-strategy-001" not in serialized
    assert "Unauthorized roles must never receive this body" not in serialized


def test_memory_type_literal_is_exactly_pdr_four_terms():
    assert set(get_args(MemoryType)) == {"episodic", "semantic", "procedural", "working"}
    assert len(get_args(MemoryType)) == 4


def test_demo_substrate_uses_pdr_memory_terms():
    memory_types = {record.memory_type for record in build_demo_substrate()}
    assert memory_types == {"episodic", "semantic", "procedural", "working"}


def test_representative_source_kinds_match_pdr_memory_mapping():
    observed = {}
    for record in build_demo_substrate():
        observed.setdefault(record.memory_type, set()).add(record.source_kind)

    assert observed["working"] == MEMORY_TYPE_SOURCE_KINDS["working"]
    assert MEMORY_TYPE_SOURCE_KINDS["semantic"].issubset(observed["semantic"])
    assert MEMORY_TYPE_SOURCE_KINDS["procedural"].issubset(observed["procedural"])
    assert MEMORY_TYPE_SOURCE_KINDS["episodic"].issubset(observed["episodic"])


def test_working_memory_never_uses_fact_store():
    assert all(
        not (record.memory_type == "working" and record.source_kind == "fact_store")
        for record in build_demo_substrate()
    )


def test_quant_strategy_reviewer_blocks_episodic_source_kinds():
    packet = retrieve_for_role(
        "quant_strategy_reviewer",
        "episodic state db session message snapshot session search tool trace prior run",
        limit=20,
    )
    blocked = set(packet.telemetry["blocked_source_ids"])
    episodic_records = [
        record for record in build_demo_substrate() if record.memory_type == "episodic"
    ]

    assert {record.source_kind for record in episodic_records} == MEMORY_TYPE_SOURCE_KINDS[
        "episodic"
    ]
    assert {record.source_id for record in episodic_records}.issubset(blocked)
    assert all(hit.citation["memory_type"] != "episodic" for hit in packet.hits)


def test_demo_substrate_is_synthetic():
    serialized = json.dumps([record.__dict__ for record in build_demo_substrate()])
    banned = [
        "/home/" + "flavorbot",
        "Obsi" + "dian",
        "OPENAI" + "_API_KEY",
        "ANTHROPIC" + "_API_KEY",
        "current" + "_weights",
    ]
    for token in banned:
        assert token not in serialized
