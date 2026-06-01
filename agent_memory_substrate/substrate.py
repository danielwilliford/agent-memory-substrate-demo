from __future__ import annotations

import time
from dataclasses import asdict

from .models import BlockedHit, MemoryRecord, RetrievalHit, RetrievalPacket, RolePolicy
from .scoring import deterministic_similarity, matched_tags

ROLE_POLICIES = {
    "research_scout": RolePolicy(
        role="research_scout",
        allowed_memory_types=["episodic", "semantic", "procedural", "working"],
        allowed_sensitivities=["public", "internal"],
    ),
    "quant_strategy_reviewer": RolePolicy(
        role="quant_strategy_reviewer",
        allowed_memory_types=["semantic", "procedural", "working"],
        allowed_sensitivities=["public", "internal"],
    ),
    "security_reviewer": RolePolicy(
        role="security_reviewer",
        allowed_memory_types=["episodic", "semantic", "procedural", "working"],
        allowed_sensitivities=["public", "internal", "restricted"],
    ),
}


def build_demo_substrate() -> list[MemoryRecord]:
    return [
        MemoryRecord(
            source_id="working-run-context-001",
            title="Current run task frame",
            memory_type="working",
            source_kind="run_context",
            content=(
                "Working memory is the current run/task frame: active role, user task, "
                "selected context ids, blocked ids, token budget, and review boundary. "
                "It is compact current context, not fact_store memory."
            ),
            tags=["working memory", "run context", "task frame", "review boundary"],
            allowed_roles=[
                "research_scout",
                "quant_strategy_reviewer",
                "security_reviewer",
            ],
            source_ref="examples/working_context.json",
        ),
        MemoryRecord(
            source_id="working-injected-context-001",
            title="Injected profile-local context",
            memory_type="working",
            source_kind="injected_context",
            content=(
                "Working memory also covers compact injected MEMORY.md and USER.md "
                "surfaces plus profile-local current context for this run."
            ),
            tags=["working memory", "injected context", "memory md", "user md"],
            allowed_roles=[
                "research_scout",
                "quant_strategy_reviewer",
                "security_reviewer",
            ],
            source_ref="examples/memory.md",
        ),
        MemoryRecord(
            source_id="semantic-fact-001",
            title="Stable semantic fact",
            memory_type="semantic",
            source_kind="fact_store",
            content=(
                "Semantic memory includes fact store entries: durable project facts, "
                "source pointers, and stable assertions queryable across runs."
            ),
            tags=["semantic memory", "fact store", "stable facts", "source pointers"],
            allowed_roles=["research_scout", "quant_strategy_reviewer", "security_reviewer"],
            source_ref="examples/semantic/fact-store-record.json",
        ),
        MemoryRecord(
            source_id="semantic-role-index-001",
            title="Role memory routing contract",
            memory_type="semantic",
            source_kind="role_index",
            content=(
                "Semantic memory includes the role-memory index: role aliases, "
                "canonical note pointers, profile routing, include rules, and avoid rules."
            ),
            tags=["semantic memory", "role index", "routing", "canonical notes"],
            allowed_roles=[
                "research_scout",
                "quant_strategy_reviewer",
                "security_reviewer",
            ],
            source_ref="examples/semantic/role-memory-index.json",
        ),
        MemoryRecord(
            source_id="semantic-profile-catalog-001",
            title="Profile catalog entry",
            memory_type="semantic",
            source_kind="profile_catalog",
            content=(
                "Semantic profile catalog memory lists available synthetic profiles, "
                "their roles, and which canonical notes or procedures they may load."
            ),
            tags=["semantic memory", "profile catalog", "profiles", "routing"],
            allowed_roles=["research_scout", "quant_strategy_reviewer", "security_reviewer"],
            source_ref="examples/semantic/profile-catalog.json",
        ),
        MemoryRecord(
            source_id="semantic-canonical-note-001",
            title="Canonical review boundary note",
            memory_type="semantic",
            source_kind="canonical_note",
            content=(
                "Canonical notes are semantic memory when they preserve durable "
                "review boundaries, definitions, assumptions, and citation expectations."
            ),
            tags=["semantic memory", "canonical note", "review boundary", "citations"],
            allowed_roles=["research_scout", "quant_strategy_reviewer", "security_reviewer"],
            source_ref="examples/semantic/canonical-review-boundary.md",
        ),
        MemoryRecord(
            source_id="vault-research-001",
            title="Synthetic research vectorization note",
            memory_type="semantic",
            source_kind="vault_note",
            content=(
                "Semantic vault notes preserve synthetic research ideas, assumptions, "
                "citation freshness, source trails, and implementation boundaries."
            ),
            tags=[
                "semantic memory",
                "research ideas",
                "citation freshness",
                "source notes",
            ],
            allowed_roles=["research_scout", "quant_strategy_reviewer", "security_reviewer"],
            source_ref="examples/vault/research-vectorization-notes.md",
        ),
        MemoryRecord(
            source_id="procedure-sandbox-001",
            title="Sandbox review skill",
            memory_type="procedural",
            source_kind="skill",
            content=(
                "Procedural memory includes skills: compact role-local procedure sets "
                "for assembling synthetic paper trial packets with validation notes."
            ),
            tags=["procedural memory", "skill", "sandbox", "paper trial"],
            allowed_roles=["research_scout", "quant_strategy_reviewer"],
            source_ref="examples/procedures/sandbox-review.md",
        ),
        MemoryRecord(
            source_id="procedure-profile-map-001",
            title="Reviewer profile map",
            memory_type="procedural",
            source_kind="profile_map",
            content=(
                "Procedural profile maps bind a role to compact local procedure sets, "
                "approval gates, and review steps for safe synthetic analysis."
            ),
            tags=["procedural memory", "profile map", "approval gates", "review steps"],
            allowed_roles=["research_scout", "quant_strategy_reviewer", "security_reviewer"],
            source_ref="examples/procedures/profile-map.json",
        ),
        MemoryRecord(
            source_id="idea-sandbox-001",
            title="Paper trial runbook",
            memory_type="procedural",
            source_kind="runbook",
            content=(
                "Procedural runbook: review a synthetic strategy sandbox paper trial, "
                "check leakage, attach provenance, mark stale evidence, and stop at "
                "the human approval gate."
            ),
            tags=[
                "procedural memory",
                "runbook",
                "strategy sandbox",
                "paper trial",
                "human approval",
            ],
            allowed_roles=["research_scout", "quant_strategy_reviewer"],
            source_ref="examples/procedures/paper-trial-runbook.md",
        ),
        MemoryRecord(
            source_id="episodic-state-001",
            title="State database session row",
            memory_type="episodic",
            source_kind="state_db",
            content=(
                "Episodic memory includes state.db/session/message SQLite evidence: "
                "raw prior-run records that may support later synthesis."
            ),
            tags=["episodic memory", "state db", "sqlite", "session evidence"],
            allowed_roles=["research_scout", "security_reviewer"],
            freshness="stale",
            source_ref="examples/episodic/state-db-session.json",
        ),
        MemoryRecord(
            source_id="episodic-message-001",
            title="Prior session message",
            memory_type="episodic",
            source_kind="session_message",
            content=(
                "A synthetic prior session message is episodic evidence, not a durable "
                "fact, because it records what happened in a specific run."
            ),
            tags=["episodic memory", "session message", "prior run", "evidence"],
            allowed_roles=["research_scout", "security_reviewer"],
            source_ref="examples/episodic/session-message.json",
        ),
        MemoryRecord(
            source_id="episodic-snapshot-001",
            title="Prior run snapshot",
            memory_type="episodic",
            source_kind="snapshot",
            content=(
                "Snapshots are episodic memory when they capture a bounded prior-run "
                "state for audit or reconstruction."
            ),
            tags=["episodic memory", "snapshot", "prior run", "audit"],
            allowed_roles=["research_scout", "security_reviewer"],
            source_ref="examples/episodic/snapshot.json",
        ),
        MemoryRecord(
            source_id="idea-stale-001",
            title="Session-search stale evidence",
            memory_type="episodic",
            source_kind="session_search",
            content=(
                "Session-search evidence found an older episodic implementation note. "
                "It is stale and requires synthesis before durable memory promotion."
            ),
            tags=[
                "episodic memory",
                "session search",
                "older episodic",
                "implementation note",
                "refresh required",
            ],
            allowed_roles=["research_scout", "security_reviewer"],
            freshness="stale",
            source_ref="examples/episodic/session-search.json",
        ),
        MemoryRecord(
            source_id="episodic-tool-trace-001",
            title="Prior ingestion tool trace",
            memory_type="episodic",
            source_kind="tool_trace",
            content=(
                "A synthetic prior-run tool trace recorded status, latency, source id, "
                "and outcome as event history. Current retrieval telemetry is separate."
            ),
            tags=["episodic memory", "tool trace", "prior run", "event history"],
            allowed_roles=["research_scout", "security_reviewer"],
            source_ref="examples/tool_traces/ingestion-run.json",
        ),
        MemoryRecord(
            source_id="restricted-strategy-001",
            title="Restricted strategy boundary note",
            memory_type="semantic",
            source_kind="vault_note",
            content=(
                "Restricted synthetic content. Unauthorized roles must never receive "
                "this body in retrieval packets."
            ),
            tags=["restricted", "strategy", "private", "semantic memory"],
            allowed_roles=["security_reviewer"],
            sensitivity="restricted",
            source_ref="examples/vault/restricted-strategy-note.md",
        ),
    ]


def _block_reason(policy: RolePolicy, record: MemoryRecord) -> str | None:
    if record.memory_type not in policy.allowed_memory_types:
        return "memory_type_not_allowed"
    if record.sensitivity not in policy.allowed_sensitivities:
        return "sensitivity_not_allowed"
    if policy.role not in record.allowed_roles:
        return "role_not_allowed"
    return None


def retrieve_for_role(
    role: str,
    query: str,
    records: list[MemoryRecord] | None = None,
    limit: int = 4,
) -> RetrievalPacket:
    if role not in ROLE_POLICIES:
        raise ValueError(f"unknown role: {role}")
    start = time.perf_counter()
    policy = ROLE_POLICIES[role]
    if records is None:
        records = build_demo_substrate()
    hits: list[RetrievalHit] = []
    blocked: list[BlockedHit] = []
    memory_types_checked = sorted({record.memory_type for record in records})
    source_kinds_checked = sorted({record.source_kind for record in records})

    for record in records:
        reason = _block_reason(policy, record)
        if reason:
            public_score = deterministic_similarity(
                query,
                f"{record.source_id} {record.memory_type} {record.source_kind}",
                record.tags,
            )
            if public_score > 0:
                blocked_ref = f"blocked_{len(blocked) + 1:03d}"
                blocked.append(BlockedHit(blocked_ref=blocked_ref, reason=reason))
            continue

        score = deterministic_similarity(query, f"{record.title} {record.content}", record.tags)
        if score <= 0:
            continue
        hits.append(
            RetrievalHit(
                source_id=record.source_id,
                title=record.title,
                score=score,
                citation=record.public_citation(),
                content=record.content,
                matched_tags=matched_tags(query, record.tags),
            )
        )

    hits.sort(key=lambda hit: hit.score, reverse=True)
    selected = hits[:limit]
    latency_ms = round((time.perf_counter() - start) * 1000, 3)
    return RetrievalPacket(
        role=role,
        query=query,
        hits=selected,
        blocked=blocked,
        telemetry={
            "role": role,
            "query": query,
            "retrieved_source_ids": [hit.source_id for hit in selected],
            "blocked_refs": [hit.blocked_ref for hit in blocked],
            "latency_ms": latency_ms,
            "memory_types_checked": memory_types_checked,
            "source_kinds_checked": source_kinds_checked,
            "review_required": any(hit.citation.get("freshness") == "stale" for hit in selected)
            or bool(blocked),
        },
    )


def build_review_packet(
    role: str,
    query: str,
    records: list[MemoryRecord] | None = None,
) -> dict[str, object]:
    retrieval = retrieve_for_role(role, query, records=records)
    stale = [hit.source_id for hit in retrieval.hits if hit.citation.get("freshness") == "stale"]
    return {
        "mode": "harness_agnostic_memory_substrate",
        "role": role,
        "task": query,
        "retrieval": retrieval.to_dict(),
        "citations": [hit.citation for hit in retrieval.hits],
        "stale_source_ids": stale,
        "human_decision_boundary": (
            "Retrieved context may support a review packet, but implementation "
            "or operational changes require human approval."
        ),
        "adapter_shape": {
            "prefetch_context": [asdict(hit) for hit in retrieval.hits],
            "blocked_context": [asdict(hit) for hit in retrieval.blocked],
            "telemetry": retrieval.telemetry,
        },
    }
