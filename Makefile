.PHONY: test lint format-check demo verify-demo reports verify clean

test:
	python -m pytest

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

demo:
	python -m agent_memory_substrate.demo

verify-demo:
	python -m agent_memory_substrate.demo > /tmp/agent-memory-substrate-demo-packet.json

reports:
	python -m agent_memory_substrate.control_reports --out examples/control_reports

verify: reports test lint format-check verify-demo

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
