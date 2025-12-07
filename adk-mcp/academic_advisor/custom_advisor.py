from typing import Any, Dict, List
from rasa.agents.protocol.mcp.mcp_open_agent import MCPOpenAgent
from rasa.agents.schemas import AgentInput, AgentOutput, AgentToolResult
from rasa_sdk.events import SlotSet
import google.genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

class AcademicAdvisorAgent(MCPOpenAgent):
    
    SYSTEM_PROMPT = """
You are a friendly, highly knowledgeable career advisor at a UK university, helping undergraduate students navigate their career paths.

## Your Core Responsibilities
- Provide career guidance tailored to the **UK job market** and higher education system.
- Offer advice suitable for **undergraduate students** (typically ages 18-22).
- Be warm, encouraging, and realistic about opportunities and challenges.

## 🇬🇧 UK-Specific Context
- Reference UK job market trends, graduate schemes (e.g., Big 4, FMCG rotational programs).
- Mention UK resources: Prospects, TargetJobs, RateMyPlacement.
- Consider UK work visa requirements for international students.

## 🎨 Response Structure
1. Brief acknowledgment (1 sentence)
2. Tailored advice (2-3 paragraphs, 100-200 words)
3. "Your Next Steps" - Bulleted list of 2-3 actions
4. UK Resources - 1-2 relevant links
5. Encouragement - One supportive closing line
"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ CORRECT: Initialize client exactly as in your custom action
        api_key = os.getenv("GEMINI_SEARCH_GROUNDING")
        if not api_key:
            raise ValueError("GEMINI_SEARCH_GROUNDING environment variable not set")
        
        self.client = google.genai.Client(api_key=api_key)
        
    def get_custom_tool_definitions(self) -> List[Dict[str, Any]]:
        """Define the career advice tool"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_career_advice",
                    "description": "Generate personalized UK career advice using Google Search grounding",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "student_profile": {
                                "type": "string",
                                "description": "Student's major, year, interests, and context"
                            },
                            "query": {
                                "type": "string",
                                "description": "The specific career question or topic"
                            }
                        },
                        "required": ["student_profile", "query"],
                        "additionalProperties": False
                    },
                    "strict": True
                },
                "tool_executor": self._generate_career_advice
            }
        ]
    
    async def _generate_career_advice(self, arguments: Dict[str, Any]) -> AgentToolResult:
        """Execute career advice generation with Gemini + Search"""
        try:
            student_profile = arguments.get("student_profile", "")
            query = arguments.get("query", "")
            
            # Build prompt
            user_prompt = f"""
## Student Profile
{student_profile}

## Student's Question
{query}

Generate career advice following the system instructions.
"""
            
            # ✅ CORRECT: Use the exact API pattern from your custom action
            grounding_tool = types.Tool(google_search=types.GoogleSearch())

            config = types.GenerateContentConfig(
                tools=[grounding_tool],
                # temperature=0.7,
                top_p=0.7,
                max_output_tokens=500,
                system_instruction=self.SYSTEM_PROMPT,
            )

            response = self.client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=user_prompt,
                config=config,
            )
            
            # ✅ CORRECT: Check response validity as in your custom action
            if response.text:
                return AgentToolResult(
                    tool_name="generate_career_advice",
                    result=response.text,
                    is_error=False
                )
            else:
                raise Exception("Empty or invalid response from Gemini API.")
            
        except Exception as e:
            # Fallback advice on error
            fallback = self._generate_fallback_advice(arguments.get("student_profile", ""))
            
            return AgentToolResult(
                tool_name="generate_career_advice",
                result=fallback,
                is_error=False  # Don't fail - provide fallback
            )
    
    def _generate_fallback_advice(self, profile: str) -> str:
        """Generate helpful fallback when LLM fails"""
        return """
I'm having a brief technical hiccup, but let me share some general guidance!

**Immediate Steps:**
- Visit your university's career service for one-on-one guidance
- Explore opportunities on [Prospects](https://www.prospects.ac.uk)
- Connect with alumni via LinkedIn

**Resources:**
- [Prospects Career Planner](https://www.prospects.ac.uk/)
- [TargetJobs](https://www.targetjobs.co.uk)

Try asking me again in a moment!
"""
    
    async def process_input(self, input: AgentInput) -> AgentInput:
        """✅ KEY IMPROVEMENT: Manage context window by filtering slots"""
        relevant_slots = [
            "student_name", "career_interest", "current_major", 
            "year_of_study", "gpa", "has_internship", "visa_status"
        ]
        
        # Only pass relevant slots - dramatically reduces context
        input.slots = [s for s in input.slots if s.name in relevant_slots]
        
        return input
    
    async def process_output(self, output: AgentOutput) -> AgentOutput:
        """Store generated advice in slots for future reference"""
        if output.structured_results:
            events = output.events or []
            
            for result_set in output.structured_results:
                for result in result_set:
                    if result.get("tool_name") == "generate_career_advice":
                        advice_text = result.get("result", "")
                        
                        # Store full advice
                        events.append(SlotSet("last_career_advice_full", advice_text))
                        
                        # Store summary (first 200 chars)
                        summary = advice_text[:200] + "..." if len(advice_text) > 200 else advice_text
                        events.append(SlotSet("last_career_summary", summary))
            
            output.events = events
        
        return output