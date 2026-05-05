from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]

MCP_PROJECT_PATH = BASE_DIR / "services" / "mcp-server" / "main.py"

def get_mcp_config() -> dict:
    """returns the configuration for the MCP client to connect to the MCP server"""
    return {
        "doc-ai-tools": {
            "transport":"stdio",
            "command": "uv",
            "args": [
                "run",
                "fastmcp",
                "run",
                "--transport",
                "stdio",
                str(MCP_PROJECT_PATH),
            ]
        }
    }
