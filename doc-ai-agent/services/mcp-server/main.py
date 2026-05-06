from fastmcp import FastMCP
import logging

from config import configure_logging, get_settings
from tools.github.fetch_group_readme import register_fetch_group_readme_tool
from tools.search.vector_search_by_group import register_vector_search_by_group_tool
from tools.documents.crud_tools import register_crud_tools
from tools.actions.action_tools import register_action_tools
from tools.summary.summary_tool import register_summary_tool

settings = get_settings()
configure_logging(settings)

logger = logging.getLogger(__name__)

mcp = FastMCP("doc-ai-mcp-server")

# Register all tools
register_fetch_group_readme_tool(mcp)
register_vector_search_by_group_tool(mcp)
register_crud_tools(mcp)
register_action_tools(mcp)
register_summary_tool(mcp)

if __name__ == "__main__":
    logger.info("MCP Server Service starting with tools:")
    logger.info("  - fetch_group_readme: Fetch README from GitHub groups")
    logger.info("  - vector_search_by_group: Search documents in a group by vector similarity")
    logger.info("  - create_document: Create a new document with embedding")
    logger.info("  - read_document: Retrieve document details")
    logger.info("  - update_document: Update document content/metadata")
    logger.info("  - assign_document: Assign document to a group")
    logger.info("  - create_group: Create a new document group")
    logger.info("  - flag_for_human_review: Flag document for human review")
    logger.info("  - generate_summary: Generate content summary using LLM")
    mcp.run()
