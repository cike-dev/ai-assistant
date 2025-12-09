# career_search_mcp.py
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from typing import Dict, Any
from logger_utils import get_logger

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
        # enhanced_query = f"UK {focus} {query} site:prospects.ac.uk OR site:targetjobs.co.uk OR site:gradcracker.com OR site:gov.uk 2025 OR 2026"
        enhanced_query = f"UK {focus} {query} 2025 OR 2026"

        response = tavily.search(
            query=enhanced_query,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
            max_results=8
        )

        # Structured output = easy for Gemini to parse in ReAct loop
        output = {
            "summary": response.get("answer", "No direct summary available."),
            "key_facts": [
                f"{r['title']} → {r['url']}"
                for r in response.get("results", [])[:6]
            ],
            "follow_up_questions": response.get("follow_up_questions", []),
            "raw_results_count": len(response.get("results", []))
        }
        logger = get_logger("search_uk_career_info")
        logger.info(f"UK career search results for query '{enhanced_query}': {output}\n")
        return output

    except Exception as e:
        raise ToolError(f"Tavily search failed: {str(e)}")


# ──────────────────────────────────────────────────────────────
# Tool for Wolverhampton University content extraction (RAG support)
# ──────────────────────────────────────────────────────────────
@server.tool()
def extract_wlv_campus_info(query: str) -> Dict[str, Any]:
    """
    Extract web content from University of Wolverhampton website (wlv.ac.uk).
    Specialized for school/campus information to support RAG responses.

    Args:
        query: Specific topic or search within the wlv.ac.uk site (e.g., "student life", "academic support")
    """
    try:
        # Force search within wlv.ac.uk domain
        enhanced_query = f"site:wlv.ac.uk {query}"

        response = tavily.search(
            query=enhanced_query,
            search_depth="basic",
            include_domains=["wlv.ac.uk"],
            include_raw_content=True,  # Get full content for RAG
            max_results=5
        )

        results = response.get("results", [])
        extracted_content = [
            {
                "title": r["title"],
                "url": r["url"],
                "content": r.get("content", "")
            }
            for r in results if r.get("content")
        ]

        logger = get_logger("extract_wlv_campus_info")
        logger.info(f"Extracted {len(extracted_content)} pages from wlv.ac.uk for query '{query}': {[page['title'] for page in extracted_content]}\n")
        
        # Structured output for easy accessibility
        output = {
            "summary": f"Extracted {len(extracted_content)} pages of content from Wolverhampton University website for '{query}'.",
            "key_facts": [f"{p['title']} → {p['url']}" for p in extracted_content],
            "extracted_content": extracted_content,  # Full content for RAG
            "total_extracted": len(extracted_content)
        }
        logger.info(f"Output sent to Rasa: \n \t{output} \n")
        return output

    except Exception as e:
        raise ToolError(f"WLV content extraction failed: {str(e)}")


# ──────────────────────────────────────────────────────────────
# Tool for UK company information retrieval
# ──────────────────────────────────────────────────────────────
@server.tool()
def get_uk_company_info(company_name: str) -> Any:
    """
    Retrieve detailed company information using Tavily's company info API.
    Focused on UK-based companies for career and job market insights.

    Args:
        company_name: Name of the UK company to retrieve information about
    """
    try:
        # Enhance query with UK focus
        enhanced_query = f"{company_name} UK"

        response = tavily.get_company_info(
            query=enhanced_query,
            country="united kingdom"
        )

        logger = get_logger("get_uk_company_info")
        logger.info(f"UK company info for '{enhanced_query}': {response}\n")
        return response

    except Exception as e:
        raise ToolError(f"UK company info retrieval failed: {str(e)}")


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
