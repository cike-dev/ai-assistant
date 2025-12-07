# career_search_mcp.py
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv()

# ──────────────────────────────────────────────────────────────
# Initialise MCP server (name shows up nicely in Rasa logs)
# ──────────────────────────────────────────────────────────────
server = FastMCP(
    name="UK Career Advisor Search Tools",
    mask_error_details=False
    )

# ──────────────────────────────────────────────────────────────
# Tavily client (fail fast if key missing)
# ──────────────────────────────────────────────────────────────
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY not found in .env")

tavily = TavilyClient(api_key=tavily_api_key)


# ──────────────────────────────────────────────────────────────
# Core tool — ONE powerful, flexible tool beats four narrow ones
# ──────────────────────────────────────────────────────────────
@server.tool()
def search_uk_career_info(
    query: str,
    focus: str = "general"  # general | salary | trends | deadlines | companies | visas
) -> Dict[str, Any]:
    """
    Search up-to-date UK career & job market information.
    Always use this before giving time-sensitive advice.

    Args:
        query: Main search (e.g. "software engineer London 2026 graduate schemes")
        focus: Helps prioritise results → salary | trends | deadlines | companies | visas | pathways
    """
    try:
        # Force UK focus + higher quality
        enhanced_query = f"UK {focus} {query} site:prospects.ac.uk OR site:targetjobs.co.uk OR site:gradcracker.com OR site:gov.uk 2025 OR 2026"

        response = tavily.search(
            query=enhanced_query,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
            max_results=8
        )

        # Structured output = easy for Gemini to parse in ReAct loop
        return {
            "summary": response.get("answer", "No direct summary available."),
            "key_facts": [
                f"{r['title']} → {r['url']}" 
                for r in response.get("results", [])[:6]
            ],
            "follow_up_questions": response.get("follow_up_questions", []),
            "raw_results_count": len(response.get("results", []))
        }

    except Exception as e:
        raise ToolError(f"Tavily search failed: {str(e)}")


# ──────────────────────────────────────────────────────────────
# Optional: tiny health-check tool (great for debugging in Rasa inspect)
# ──────────────────────────────────────────────────────────────
@server.tool()
def ping() -> str:
    """Simple health check — returns 'pong' if server is alive"""
    return "pong – UK Career Search MCP is ready!"


# ──────────────────────────────────────────────────────────────
# Run server (use streamable-http for best Rasa Pro compatibility)
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # print("UK Career Search MCP Server starting on http://localhost:8080")
    server.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8080,
        stateless_http=False
    )