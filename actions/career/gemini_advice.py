"""
Refactored Gemini Career Advice Actions for Rasa
- Loads .env automatically
- Uses unified client loader
- Handles missing API keys gracefully
- Centralized config + error handling
- Cleaner separation of responsibilities
"""

import os
from typing import Any, Text, Dict, List
from dotenv import load_dotenv

# from google import genai
import google.genai 
from google.genai import types
from google.api_core import retry
from google.genai.errors import APIError

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.general.logger_utils import get_logger

# --------------------------------------------------
# Load .env before anything else
# --------------------------------------------------
load_dotenv()

logger = get_logger("GeminiCareerAdvice")

# --------------------------------------------------
# Centralized Gemini Client Loader
# --------------------------------------------------
def load_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_SEARCH_GROUNDING")

    if not api_key:
        logger.error("GEMINI_SEARCH_GROUNDING is missing in environment variables.")
        return None

    try:
        client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized successfully.")
        return client
    except Exception as e:
        logger.error(f"Error initializing Gemini client: {e}")
        return None

# --------------------------------------------------
# Base Action Class - Shared Utilities
# --------------------------------------------------
class GeminiBaseAction(Action):
    SYSTEM_PROMPT = """
You are a warm, encouraging career counsellor at the University of Wolverhampton.
Speak naturally, with warmth and occasional emojis.
Focus on UK job market trends (2025), actionable advice, and practical insights.
"""
    def name(self) -> str:
        return "gemini_base_action"

    def __init__(self) -> None:
        super().__init__()
        self.client = load_gemini_client()

        # --- RETRY POLICY ADDED HERE ---
        self.retry_policy = retry.Retry(
            predicate=lambda e: isinstance(e, APIError) and e.code in {429, 503},
            initial=1.0,       # wait 1s on first retry
            maximum=6.0,       # max wait per retry = 6 sec
            multiplier=2.0,    # exponential backoff
            deadline=12.0      # TOTAL retry time = 12 sec max (safe for Rasa)
        )

    def safe_generate(self, model: str, user_prompt: str, use_system_prompt=True):
        if not self.client:
            logger.error("Gemini client unavailable during generation.")
            return None

        try:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())

            config = types.GenerateContentConfig(
                tools=[grounding_tool],
                temperature=0.7,
                top_p=0.8,
                max_output_tokens=200,
                system_instruction=self.SYSTEM_PROMPT if use_system_prompt else None,
            )

            logger.info("Sending prompt to Gemini API...")

            response = self.client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config,
            )

            logger.info("Gemini response received.")
            return response

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None

    def format_response(self, response):
        if not response or not response.text:
            return None
        return response.text

# --------------------------------------------------
# Main Career Advice Action
# --------------------------------------------------
class ActionGiveCareerAdvice(GeminiBaseAction):
    def name(self) -> str:
        return "action_give_career_advice"

    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]):
        
        logger.info("Starting Career Advice action...")

        # Extract slots
        major = tracker.get_slot("current_major") or "your field of study"
        interest = tracker.get_slot("career_interest") or "your career interests"
        year = tracker.get_slot("year_of_study") or "your year"
        gpa = tracker.get_slot("gpa") or "N/A"

        internship_flag = str(tracker.get_slot("has_internship") or "").lower() in ["true", "yes", "y", "1"]
        internship_text = (
            "I have some internship experience that helped me a lot." if internship_flag
            else "I'm looking for entry-level opportunities to start my journey."
        )

        user_prompt = f"""
I'm a {year} {major} student with a GPA of {gpa}, interested in {interest}.
{internship_text}

Could you walk me through what opportunities exist in the UK and how I can best prepare for this path?
"""

        response = self.safe_generate("gemini-2.5-flash", user_prompt)
        final_text = self.format_response(response)

        if not final_text:
            dispatcher.utter_message(text="I'm having trouble accessing updated career insights right now. Try again soon 😊.")
            return []

        dispatcher.utter_message(text=final_text)

        # Update history
        advice_history = tracker.get_slot("advice_history") or []
        if not isinstance(advice_history, list):
            advice_history = [advice_history]
        advice_history.append(final_text)

        return [
            SlotSet("last_career_summary", final_text),
            SlotSet("advice_history", advice_history),
        ]

# --------------------------------------------------
# Follow-up Career Advice Action
# --------------------------------------------------
class ActionFollowupCareerAdvice(GeminiBaseAction):
    def name(self) -> str:
        return "action_followup_career_advice"

    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]):
        
        logger.info("Starting Follow-up Advice action...")

        history = tracker.get_slot("advice_history") or []
        last_summary = tracker.get_slot("last_career_summary")
        followup = tracker.get_slot("followup_question")

        if not last_summary:
            dispatcher.utter_message(text="I don't seem to have previous advice stored yet. What would you like to know?")
            return []

        prompt = f"""
The student previously received this advice:

{last_summary}

Now they're asking: "{followup}"

Please expand naturally on this, keeping your warm, encouraging tone and UK-focused guidance.
Here is the full advice history:
{history}
"""

        response = self.safe_generate("gemini-2.5-flash", prompt)
        final_text = self.format_response(response)

        if not final_text:
            dispatcher.utter_message(text="I couldn't expand on that right now. Could you try rephrasing your question?")
            return []

        dispatcher.utter_message(text=final_text)

        # Update history
        advice_history = history if isinstance(history, list) else [history]
        advice_history.append(final_text)

        return [
            SlotSet("last_career_summary", final_text),
            SlotSet("advice_history", advice_history),
        ]
