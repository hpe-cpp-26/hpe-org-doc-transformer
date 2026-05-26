.PHONY: mcp-dev orchestrator seed

mcp-dev:
	uv run fastmcp dev inspector services/mcp-server/main.py

orchestrator:
	uv run python3 services/orchestrator/main.py

seed:
	uv run python3 scripts/seed_dummy_data.py

