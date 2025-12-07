from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

server = FastMCP("ai-assistant-server")

# Initialize Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY environment variable must be set")

tavily_client = TavilyClient(api_key=tavily_api_key)


@server.tool()
def search_job_market_trends(query: str) -> str:
    """Search for job market trends. Args: query (description of the job field or industry)"""
    try:
        response = tavily_client.search(
            query=f"job market trends {query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = "\n".join([f"- {result['title']}: {result['url']}" for result in response.get("results", [])])
        return answer + "\n\n" + results if answer else results
    except Exception as e:
        return f"Error searching job market trends: {str(e)}"


@server.tool()
def find_salary_data(query: str) -> str:
    """Find salary data for a specific role. Args: query (job title, role, or skill set)"""
    try:
        response = tavily_client.search(
            query=f"salary data {query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = "\n".join([f"- {result['title']}: {result['url']}" for result in response.get("results", [])])
        return answer + "\n\n" + results if answer else results
    except Exception as e:
        return f"Error finding salary data: {str(e)}"


@server.tool()
def get_industry_insights(query: str) -> str:
    """Get insights about an industry. Args: query (industry name or sector)"""
    try:
        response = tavily_client.search(
            query=f"industry insights {query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = "\n".join([f"- {result['title']}: {result['url']}" for result in response.get("results", [])])
        return answer + "\n\n" + results if answer else results
    except Exception as e:
        return f"Error getting industry insights: {str(e)}"


@server.tool()
def search_career_paths(query: str) -> str:
    """Search for career paths and advancement. Args: query (current role, field, or starting point)"""
    try:
        response = tavily_client.search(
            query=f"career paths {query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = "\n".join([f"- {result['title']}: {result['url']}" for result in response.get("results", [])])
        return answer + "\n\n" + results if answer else results
    except Exception as e:
        return f"Error searching career paths: {str(e)}"


if __name__ == "__main__":
    print("Starting MCP Server for AI Assistant with Tavily Search Tools...")
    print("Settings:", (i for i in server.settings))
    server.run()
    
