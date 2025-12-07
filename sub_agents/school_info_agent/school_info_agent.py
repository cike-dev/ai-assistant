from typing import Any, Dict, List
from rasa.agents.protocol.mcp.mcp_open_agent import MCPOpenAgent
from rasa.agents.schemas import AgentInput, AgentOutput, AgentToolResult
import os
from dotenv import load_dotenv

load_dotenv()

class SchoolInfoSearchAgent(MCPOpenAgent):

    SYSTEM_PROMPT = """School information retrieval propt"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_custom_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        No custom tool definitions needed - using MCP server tools
        The MCP server provides: search_job_market_trends, find_salary_data,
        get_industry_insights, search_career_paths
        """
        return []

    async def process_input(self, input: AgentInput) -> AgentInput:
        """Process input before sending to tools"""
        return input

    async def process_output(self, output: AgentOutput) -> AgentOutput:
        """Process output from tools"""
        return output
