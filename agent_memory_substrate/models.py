from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Literal

MemoryType = Literal["episodic", "semantic", "procedural", "working"]
SourceKind = Literal[
    "run_context",
    "injected_context",
    "fact_store",
    "role_index",
    "profile_catalog",
    "canonical_note",
    "vault_note",
    "skill",
    "profile_map",
    "runbook",
    "state_db",
    "session_message",
    "snapshot",
    "session_search",
    "tool_trace",
]
Sensitivity = Literal["public", "internal", "restricted"]
Freshness = Literal["fresh", "stale", "unknown"]


MEMORY_TYPE_SOURCE_KINDS: dict[str, set[str]] = {
    "working": {"run_context", "injected_context"},
    "semantic": {
        "fact_store",
        "role_index",
        "profile_catalog",
        "canonical_note",
        "vault_note",
    },
    "procedural": {"skill", "profile_map", "runbook"},
    "episodic": {
        "state_db",
        "session_message",
        "snapshot",
        "session_search",
        "tool_trace",
    },
}


@dataclass(frozen=True)
class MemoryRecord:
    source_id: str
    title: str
    memory_type: MemoryType
    source_kind: SourceKind
    content: str
    tags: list[str]
    allowed_roles: list[str]
    sensitivity: Sensitivity = "public"
    freshness: Freshness = "fresh"
    source_ref: str = "synthetic"
    created_on: str = field(default_factory=lambda: date.today().isoformat())

    def public_citation(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "memory_type": self.memory_type,
            "source_kind": self.source_kind,
            "freshness": self.freshness,
            "source_ref": self.source_ref,
        }


@dataclass(frozen=True)
class RolePolicy:
    role: str
    allowed_memory_types: list[MemoryType]
    allowed_sensitivities: list[Sensitivity]
    can_request_human_review: bool = True


@dataclass(frozen=True)
class RetrievalHit:
    source_id: str
    title: str
    score: float
    citation: dict[str, str]
    content: str
    matched_tags: list[str]


@dataclass(frozen=True)
class BlockedHit:
    source_id: str
    reason: str


@dataclass(frozen=True)
class RetrievalPacket:
    role: str
    query: str
    hits: list[RetrievalHit]
    blocked: list[BlockedHit]
    telemetry: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "role": self.role,
            "query": self.query,
            "hits": [asdict(hit) for hit in self.hits],
            "blocked": [asdict(hit) for hit in self.blocked],
            "telemetry": self.telemetry,
        }
