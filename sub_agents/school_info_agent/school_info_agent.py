from typing import Any, Dict, List
from rasa.agents.protocol.mcp.mcp_open_agent import MCPOpenAgent
from rasa.agents.schemas import AgentInput, AgentOutput, AgentToolResult
from rasa_sdk.events import Event, SlotSet

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

    # async def process_output(self, output: AgentOutput) -> AgentOutput:
    #     """Process output from tools"""
    #     return output
    
    # async def process_output(self, output: AgentOutput) -> AgentOutput:
    #     """Process the MCP tool output and extract structured data."""
        
    #     # The structured_results contains all tool invocation results
    #     if output.structured_results:
    #         parsed_results = []
            
    #         # Iterate through the tool results
    #         for result_set in output.structured_results:
    #             for result in result_set:
    #                 # Your tool output is a list of dicts with title, url, content
    #                 if isinstance(result, dict):
    #                     parsed_results.append({
    #                         'title': result.get('title', ''),
    #                         'url': result.get('url', ''),
    #                         'content': result.get('content', '')
    #                     })
            
    #         # Store the parsed results in a slot
    #         if parsed_results:
    #             output.events = output.events or []
    #             output.events.append(
    #                 SlotSet("search_results", parsed_results)
    #             )
        
    #     return output



    # async def process_output(self, output: AgentOutput) -> AgentOutput:
    #     """Process the MCP tool output and extract structured data."""
        
    #     if output.structured_results:
    #         parsed_results = []
            
    #         # structured_results is List[List[Dict]]
    #         for result_set in output.structured_results:
    #             if isinstance(result_set, list):
    #                 for item in result_set:
    #                     if isinstance(item, dict):
    #                         parsed_results.append({
    #                             'title': item.get('title', ''),
    #                             'url': item.get('url', ''),
    #                             'content': item.get('content', '')
    #                         })
            
    #         # Store parsed results in a slot
    #         if parsed_results:
    #             if output.events is None:
    #                 output.events = []
    #             output.events.append({
    #                 "event": "slot",
    #                 "name": "specialized_result",
    #                 "value": parsed_results
    #             })
        
    #     return output
