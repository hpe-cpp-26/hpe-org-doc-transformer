from fastmcp import FastMCP
import logging

from config import configure_logging, get_settings
from tools.github.fetch_group_readme import register_fetch_group_readme_tool
from tools.search.search_group_chunks import register_search_group_chunks_tool

settings = get_settings()
configure_logging(settings)

logger = logging.getLogger(__name__)

mcp = FastMCP("doc-ai-mcp-server")
register_fetch_group_readme_tool(mcp)
# register_search_group_chunks_tool(mcp)

if __name__ == "__main__":
    logger.info("MCP Server Service starting")
    mcp.run()
