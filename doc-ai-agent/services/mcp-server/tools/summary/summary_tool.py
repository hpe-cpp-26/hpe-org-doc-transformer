from fastmcp import FastMCP
import logging

from agent.schema import (
    GenerateSummaryRequest,
    GenerateSummaryResponse,
)

logger = logging.getLogger(__name__)


def register_summary_tool(mcp: FastMCP):
    """Register summary generation tool."""

    @mcp.tool
    async def generate_summary(request: GenerateSummaryRequest) -> GenerateSummaryResponse:
        """
        Generate a summary of document or group content.
        
        Uses an LLM to create a concise summary of the provided content.
        Can optionally focus on specific aspects like key points, architecture,
        team information, etc.
        
        Args:
            request.content: The content to summarize
            request.max_length: Maximum summary length in words (default 500)
            request.focus: Optional focus area for the summary
            
        Returns:
            Generated summary with original and summary lengths
        """
        from agent.llm import get_llm

        content = request.content
        max_length = request.max_length
        focus = request.focus

        logger.info(
            "Generating summary (max_length: %d, focus: %s)",
            max_length,
            focus or "general",
        )

        try:
            # Build the prompt
            focus_instruction = ""
            if focus:
                focus_instruction = f"\nFocus specifically on: {focus}"

            prompt = f"""Please provide a concise summary of the following content in no more than {max_length} words.{focus_instruction}

Content:
{content}

Summary:"""

            # Get LLM client
            llm = get_llm()
            
            # Generate summary
            summary = await llm.generate(prompt)
            
            # Count words
            summary_length = len(summary.split())
            original_length = len(content.split())

            logger.info(
                "Summary generated (original: %d words, summary: %d words)",
                original_length,
                summary_length,
            )

            return GenerateSummaryResponse(
                original_length=original_length,
                summary=summary.strip(),
                summary_length=summary_length,
            )

        except Exception as exc:
            logger.error("Failed to generate summary: %s", exc)
            raise
