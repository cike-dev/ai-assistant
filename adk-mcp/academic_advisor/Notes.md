### How Rasa Sub-Agents Work with MCP

Rasa sub-agents connect to MCP servers that expose tools. The sub-agent (powered by an LLM like Gemini) then decides which tools to call based on the conversation context.

For this use case, we'll need:
    - An MCP server that exposes a Google Search tool
    - A ReAct sub-agent configured to use Gemini as its LLM
    - The sub-agent connects to the MCP server and can invoke the search tool

#### Implementation Steps
1. Set Up an MCP Server with Google Search

First, we need an MCP server that provides a Google Search tool. We could:
    - Use an existing MCP server that supports search (check the MCP server directory)
    - Build your own MCP server that wraps Google Search API

Define the server in endpoints.yml:

```yml
mcp_servers:
  - name: search_server
    url: http://localhost:8080
    type: http
```

2. Configure the ReAct Sub-Agent

Create a sub-agent folder structure:

your_project/  
├── config.yml  
├── domain/  
├── data/flows/  
└── sub_agents/  
    └── academic_advisor/  
        ├── config.yml  
        └── prompt_template.jinja2  # optional  

Configure `sub_agents/academic_advisor/config.yml`:  

```yml
# Basic agent information
agent:
  name: academic_advisor
  description: "Agent that provides academic advice using current information from web searches"

# ReAct-specific configuration
configuration:
  llm:  # Configure Gemini as your LLM
    model-group: gemini-pro  # or your specific Gemini model
  prompt_template: sub_agents/academic_advisor/prompt_template.jinja2  # optional
  timeout: 30
  max_retries: 3

# MCP server connections
connections:
  mcp_servers:
    - name: search_server
      include_tools:
        - google_search  # The specific search tool from your MCP server
```


3. Configure Gemini in Your Main Config

In your main config.yml, configure Gemini access:

```yml
# Example LLM configuration for Gemini
llms:
  gemini-pro:
    type: google
    model: gemini-1.5-pro
    api_key: ${GOOGLE_API_KEY}
```

4. Invoke the Sub-Agent from Your Flow

Create flows for your two services:

```yml
flows:
  campus_queries:
    description: Handle student campus-related queries and confusions
    steps:
      - collect: query_type
        description: What would you like help with?
      - action: handle_campus_query

  academic_support:
    description: Provide academic advice and support to students
    steps:
      - collect: academic_question
        description: What academic topic do you need help with?
      - call: academic_advisor  # Invokes the ReAct sub-agent
        exit_if:
          - slots.advice_provided is True
```


Addressing the "Overwhelmed Model" Issue

To prevent the model from getting overwhelmed, you can customize the input processing:

```python
from rasa.agents.protocol.mcp.mcp_open_agent import MCPOpenAgent
from rasa.agents.schemas import AgentInput

class AcademicAdvisor(MCPOpenAgent):
    async def process_input(self, input: AgentInput) -> AgentInput:
        # Filter to only academic-relevant slots
        filtered_slots = [
            slot for slot in input.slots
            if slot.name in ["academic_question", "subject_area", "student_level"]
        ]
        
        return AgentInput(
            id=input.id,
            user_message=input.user_message,
            slots=filtered_slots,  # Only share necessary context
            conversation_history=input.conversation_history[-5:],  # Limit history
            events=input.events,
            metadata=input.metadata,
            timestamp=input.timestamp
        )
```

Reference this in your config:

```yaml
configuration:
  module: sub_agents.academic_advisor.custom_advisor.AcademicAdvisor
```

**The Missing Piece: MCP Server**  
The main challenge is that you need an MCP server that exposes Google Search. This isn't built into Rasa or Gemini directly. You have two options:
    - Find an existing MCP server with search capabilities
    - Build a simple MCP server that wraps Google Search API (or Serper, Tavily, etc.)


__But google_search is an internal tool available to gemini within google ai's sdk...__
Google Search is a native tool within Gemini via the Google AI SDK, not something you need to set up separately via MCP.

This actually simplifies your architecture significantly! However, there's an important consideration about how Rasa's ReAct sub-agents work with tools.


#### The Challenge

Rasa's ReAct sub-agents are designed to work with MCP (Model Context Protocol) tools23. The sub-agent architecture expects tools to be exposed through MCP servers that the agent can connect to and invoke3.

Gemini's native google_search tool works differently - it's invoked directly through the Google AI SDK when you make API calls with specific parameters.

**Recommended Solution:** Custom Python Tool

The best approach for your use case is to add a custom Python tool to your ReAct sub-agent that wraps the Gemini API with Google Search enabled2. This gives you the best of both worlds:
Implementation

1. Create a custom sub-agent module:

sub_agents/academic_advisor/custom_advisor.py:
```python
from typing import Any, Dict, List
from rasa.agents.protocol.mcp.mcp_open_agent import MCPOpenAgent
from rasa.agents.schemas import AgentInput
import google.generativeai as genai
import os

class AcademicAdvisor(MCPOpenAgent):
    
    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        # Configure Gemini with your API key
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
    def get_additional_tools(self) -> List[Dict[str, Any]]:
        """Add custom Python tools alongside MCP tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_academic_info",
                    "description": "Search for current academic information, research, or educational resources using Google Search",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query for academic information"
                            }
                        },
                        "required": ["query"],
                        "additionalProperties": False
                    },
                    "strict": True
                },
                "tool_executor": self._search_academic_info
            }
        ]
    
    async def _search_academic_info(self, query: str) -> str:
        """Execute search using Gemini with Google Search grounding."""
        try:
            # Use Gemini with Google Search grounding
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            # Enable Google Search tool
            response = model.generate_content(
                query,
                tools='google_search_retrieval'  # This enables Google Search
            )
            
            return response.text
            
        except Exception as e:
            return f"Search failed: {str(e)}"
```


2. Configure the sub-agent:

sub_agents/academic_advisor/config.yml:
```yaml
# Basic agent information
agent:
  name: academic_advisor
  description: "Agent that provides academic advice using current information from web searches"

# ReAct-specific configuration
configuration:
  llm:
    model-group: gemini-pro
  module: "sub_agents.academic_advisor.custom_advisor.AcademicAdvisor"
  timeout: 30
  max_retries: 3

# No MCP connections needed if only using custom tools
connections:
  mcp_servers: []
```

3. Set up your Environment key:  
`export GOOGLE_API_KEY=your_gemini_api_key`

4. Invoke from the flow:  

flows.yml:
```yaml
flows:
  academic_support:
    description: Provide academic advice and support to students
    steps:
      - collect: academic_question
        description: What academic topic do you need help with?
      
      - call: academic_advisor
        exit_if:
          - slots.advice_provided is True
```

How This Works:
    - The ReAct sub-agent receives the conversation context from Rasa4
    - The LLM decides when to call the search_academic_info tool based on the user's question2
    - Your custom tool invokes Gemini with google_search_retrieval enabled, which uses Google's native search capability
    - The search results are returned to the sub-agent, which can then formulate a response
    - Rasa handles all the context management, state tracking, and conversation flow automatically4