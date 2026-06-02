# Public Proof Map

This map ties the public memory-substrate claims to files a reviewer can inspect and commands they can run locally.

| Claim | Proof surface | Verification |
| --- | --- | --- |
| The demo uses the exact PDR memory terms: `working`, `semantic`, `procedural`, and `episodic`. | `agent_memory_substrate/models.py`, `agent_memory_substrate/substrate.py` | `tests/test_substrate.py::test_memory_type_literal_is_exactly_pdr_four_terms` |
| `source_kind` is separate from memory type and records concrete provenance. | `agent_memory_substrate/models.py`, synthetic files under `examples/` | `tests/test_substrate.py::test_representative_source_kinds_match_pdr_memory_mapping` |
| Role-scoped retrieval applies memory-type, sensitivity, and role checks before returning context. | `agent_memory_substrate/substrate.py` | `tests/test_substrate.py::test_quant_reviewer_gets_allowed_context_and_blocks_restricted_strategy` |
| Restricted candidates are represented as redacted blocked refs, not leaked titles or bodies. | `agent_memory_substrate/substrate.py`, `agent_memory_substrate/control_reports.py` | `tests/test_substrate.py::test_blocked_context_trace_does_not_leak_body`, `tests/test_control_reports.py` |
| Stale episodic evidence is labeled and requires review before promotion into durable memory. | `agent_memory_substrate/substrate.py`, `examples/episodic/` | `tests/test_substrate.py::test_stale_episodic_source_label_appears_in_review_packet` |
| Unknown roles fail closed without returning retrieval context. | `agent_memory_substrate/substrate.py` | `tests/test_substrate.py::test_unknown_role_fails_closed` |
| A deterministic public control report can be regenerated and schema-validated. | `agent_memory_substrate/control_reports.py`, `examples/control_reports/memory_control_report.json`, `schemas/memory_control_report.json` | `make reports`, `tests/test_control_reports.py` |
| The repo contains only synthetic public examples. | `examples/`, `agent_memory_substrate/substrate.py` | `tests/test_substrate.py::test_demo_substrate_is_synthetic` |

Run the full local proof path with:

```bash
make verify
```
