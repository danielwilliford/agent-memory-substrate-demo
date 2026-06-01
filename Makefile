.PHONY: test lint format-check demo verify clean

test:
	python -m pytest

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

demo:
	python -m agent_memory_substrate.demo

verify: test lint format-check demo

clean:
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
