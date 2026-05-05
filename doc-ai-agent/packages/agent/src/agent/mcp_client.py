from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[4]

MCP_SERVER_DIR = BASE_DIR / "services" / "mcp-server"
MCP_SERVER_ENTRY = MCP_SERVER_DIR / "main.py"

def get_mcp_config() -> dict:
    """returns the configuration for the MCP client to connect to the MCP server"""
    return {
         "doc-ai-tools": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run",
                "--project", str(MCP_SERVER_DIR),
                "python",
                str(MCP_SERVER_ENTRY),
            ]
        }
    }
