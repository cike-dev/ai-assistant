# from google.adk.agents.llm_agent import Agent

# root_agent = Agent(
#     model='gemini-2.5-flash',
#     name='root_agent',
#     description='A helpful assistant for user questions.',
#     instruction='Answer user questions to the best of your knowledge',
# )

from google.adk.planners import BuiltInPlanner
from google.adk.agents import LlmAgent

from google.genai import types
from google.genai.types import ThinkingConfig
from google.genai.types import GenerateContentConfig


# Defining content generation configuration
content_config = GenerateContentConfig(
    temperature=0.7,
    max_output_tokens=500,
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
        )
    ]
)



# =================== Thinking Configuration Example =================== #

# 1. Create a thinking configuration for the planner
thinking_config = ThinkingConfig(
    include_thoughts=False,   # Don't include Model's thoughts in the respsonse
    thinking_budget=256      # Limit the 'thinking' to 256 tokens (adjust as needed)
)
print("ThinkingConfig:", thinking_config)

# 2. Defining the planner configuration 
planner = BuiltInPlanner(
        thinking_config=thinking_config
)
print("BuiltInPlanner created.")

# Example: Defining the basic identity
career_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="capital_agent",
    description="Answers user questions about the capital city of a given country.",
    planner=planner,
    tools=[],
    generate_content_config=content_config,
    output_key="capital_response"
)

# Session and Runner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

APP_NAME = "weather_app"
USER_ID = "1234"
SESSION_ID = "session1234"

# Set up Session Management
session_service = InMemorySessionService()

# Create a new session
session = session_service.create_session(
    app_name=APP_NAME, 
    user_id=USER_ID, 
    session_id=SESSION_ID)

# Initialize a Runner for the Agent
career_agent_runner = Runner(
    agent=career_agent, 
    app_name=APP_NAME, 
    session_service=session_service)

# Agent Interaction
def call_agent(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = Runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        print(f"\nDEBUG EVENT: {event}\n")
        if event.is_final_response() and event.content:
            final_answer = event.content.parts[0].text.strip()
            print("\n🟢 FINAL ANSWER\n", final_answer, "\n")

call_agent("If it's raining in New York right now, what is the current temperature?")