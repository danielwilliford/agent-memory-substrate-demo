# Agent Memory Substrate Demo

A small public demo of harness-agnostic agent memory and retrieval boundaries.

The point is not the runner. Hermes, Pi Agent, Codex, LangGraph, or another harness can operate against the same substrate contract when the memory, retrieval, permission, telemetry, and approval surfaces are defined clearly.

This repo uses synthetic data and deterministic local similarity so a reviewer can run it without installing an agent framework, npm package, vector database, or embedding model.

## What It Shows

- memory records using the four PDR memory terms: `episodic`, `semantic`, `procedural`, and `working`
- role-scoped retrieval by memory type, sensitivity, and source permission
- blocked context telemetry without leaking restricted titles or bodies
- stale source labels, citation metadata, and concrete `source_kind` provenance
- human review packets that can be consumed by any agent harness

## Proof Surfaces

- `agent_memory_substrate/models.py`: typed memory records, exact four memory types, source-kind provenance, role policies, retrieval hits, blocked hits, and review packets
- `agent_memory_substrate/substrate.py`: demo substrate, role policy checks, retrieval packet construction, telemetry, and human-review packet adapter shape
- `agent_memory_substrate/scoring.py`: deterministic local scorer used instead of external embeddings
- `agent_memory_substrate/demo.py`: CLI entry point that emits a reviewable JSON packet
- `examples/`: synthetic working, semantic, procedural, episodic, and tool-trace examples
- `tests/`: checks for PDR mapping, role-scoped retrieval, blocked context redaction, stale labels, unknown-role fail-closed behavior, CLI output, and synthetic-data boundaries

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
make verify
```

Run only the demo packet:

```bash
python -m agent_memory_substrate.demo
```

Current local validation when reviewed:

```text
make verify
```

## PDR Memory Mapping

- `working`: compact injected `MEMORY.md`/`USER.md` surfaces, profile-local current context, and the current run/task frame. It is not `fact_store`.
- `semantic`: fact store, role-memory index, profile catalog, canonical notes, and durable vault notes.
- `procedural`: skills, profile maps, compact role-local procedure sets, runbooks, and approval gates.
- `episodic`: `state.db`/session/message SQLite evidence, session-search evidence, snapshots, and prior-run tool traces.

`source_kind` is kept separate from memory type. It records the concrete surface an item came from, such as `run_context`, `injected_context`, `fact_store`, `role_index`, `profile_catalog`, `canonical_note`, `vault_note`, `skill`, `profile_map`, `runbook`, `state_db`, `session_message`, `snapshot`, `session_search`, or `tool_trace`.

Telemetry is not a memory type. It is the retrieval audit surface for checked memory types, source kinds, selected ids, blocked ids, latency, and review signals.

Obsidian-style vault files are represented with dummy files under `examples/vault/` and `examples/semantic/`. In this demo, a vault note is `semantic` when it preserves durable project knowledge, doctrine, definitions, assumptions, or citations. A vault runbook is `procedural` when it tells the agent how to perform a task. Raw Hermes session/state history remains `episodic` until it is reviewed and synthesized into a durable note, runbook, test, or fact.


## Where This Fits

This repo stays small on purpose. It is the memory contract demo for the public project constellation:

- `agent-harness-routing-benchmark` shows profile routing, lane policy, memory policy, telemetry, and human gates.
- `agentic-ai-ops-kit` shows an applied service boundary with FastAPI, LangGraph, traces, artifacts, and approval controls.
- `agentic-finance-research-control-plane` stays separate because finance needs advisory-only boundaries, read-only adapters, and stricter public framing.

The intended composition is: this memory substrate defines how context is represented and audited; harness and ops demos can consume the same contract without absorbing the memory explainer into a larger repo.

## Demo Roles

- `research_scout` can inspect public semantic, procedural, episodic, and working memory.
- `quant_strategy_reviewer` can inspect approved semantic, procedural, and working memory, but restricted strategy content and all episodic source kinds are blocked.
- `security_reviewer` can inspect all four memory types, including access-boundary records.

## Public Boundary

All examples are synthetic. This repo contains no private datasets, live credentials, local machine paths, raw session logs, proprietary operating logic, or performance claims.

This is not a vector database, production memory service, or agent runner. It is the public contract shape: memory type, source provenance, role policy, retrieval packet, pre-retrieval access checks, redaction boundary, telemetry, citations, and human-review handoff.
