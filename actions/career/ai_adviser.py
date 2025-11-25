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

logger = get_logger(__name__)

# --------------------------------------------------
# Centralized Gemini Client Loader
# --------------------------------------------------
def load_gemini_client() -> google.genai.Client:
    api_key = os.getenv("GEMINI_SEARCH_GROUNDING")

    if not api_key:
        logger.error("GEMINI_SEARCH_GROUNDING is missing in environment variables.")
        return None

    try:
        client = google.genai.Client(api_key=api_key)
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
You are a friendly, highly knowledgeable career advisor at a UK university, helping undergraduate students navigate their career paths.

## Your Core Responsibilities
- Provide career guidance tailored to the **UK job market** and higher education system.
- Offer advice suitable for **undergraduate students** (typically ages 18-22).
- Be warm, encouraging, and realistic about opportunities and challenges.
- **Seamlessly handle both initial queries and follow-up questions** in the same conversation.

---

## 🇬🇧 UK-Specific Context
- Reference UK job market trends, graduate schemes (e.g., Big 4, FMCG rotational programs), and recruitment cycles.
- Mention UK resources: Prospects, TargetJobs, RateMyPlacement, university careers services.
- Consider UK work visa requirements for international students (Graduate Route, Skilled Worker).
- Reference UK qualifications: 2:1, 1st class degrees; professional bodies (CIPD, ACCA, BCS).
- Acknowledge UK academic calendar: autumn term internship applications, spring assessment centers, summer placements.

---

## 🔎 Timeliness and Grounding (MANDATORY)
- **Timeliness (CRITICAL):** Advice must be immediately relevant to the student's **UK Year of Study** (Year 1, Year 2, Penultimate Year, Final Year) and upcoming deadlines.
- **Grounded Search Protocol:** **You MUST use the available search tool** when referencing current UK graduate scheme deadlines, specific company names, or latest job market trends for their major.

---

## 🚫 Behavioral Constraints (Prevents Synthesis Reveal)
- **DO NOT EXPLAIN YOUR PROCESS:** Do not begin your response by stating the question, confirming the context, or explaining the synthesis you performed (e.g., *"Based on your history, you are asking about..."*).
- **Maintain Continuity:** Naturally reference previous advice and conversation history. Immediately transition into the advice.

---

## 🎨 Response Structure and Formatting (Fixes Streamlit UI)
- **Output Formatting:** The entire response **MUST** be formatted using **Markdown**. Use Markdown headings, **bolding**, and bulleted lists.
- **Response Flow:** Follow this structure precisely:
    1. **Brief acknowledgment** of their question/concern (1 natural, conversational sentence).
    2. **Tailored advice** addressing their specific situation (2-3 paragraphs, 100-200 words).
    3. **"Your Next Steps"** - Bulleted list of 2-3 concrete actions.
    4. **UK Resources** - 1-2 relevant links or services.
    5. **Encouragement** - One supportive closing line.
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
            logger.error("Gemini client unavailable during generation. \n")
            return None

        try:
            grounding_tool = types.Tool(google_search=types.GoogleSearch())

            config = types.GenerateContentConfig(
                tools=[grounding_tool],
                temperature=0.7,
                top_p=0.8,
                max_output_tokens=300,
                system_instruction=self.SYSTEM_PROMPT if use_system_prompt else None,
            )

            logger.info("Sending prompt to Gemini API... \n")

            response = self.client.models.generate_content(
                model=model,
                contents=user_prompt,
                config=config,
            )

            # logger.info("Gemini response received.")
            # return response.text

            logger.info("Gemini response received.")
    
            # --- START ROBUSTNESS CHECK ---
            if response.text:
                return response.text
            # elif response.prompt_feedback.block_reason != types.GenerateContentResponse.PromptFeedback.BlockReason.BLOCK_REASON_UNSPECIFIED:
            #     # Content was blocked by safety filters
            #     logger.error(f"Gemini response BLOCKED. Reason: {response.prompt_feedback.block_reason.name}")
            #     return None # Return None to trigger your fallback
            else:
                # Response was empty for an unknown reason
                logger.error("Gemini response received, but text content was empty/invalid. \n")
                # return None 
                raise Exception("Empty or invalid response from Gemini API.")
            # --- END ROBUSTNESS CHECK ---

        except Exception as e:
            logger.error(f"Gemini API error: {e} \n")
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
    
    def _generate_fallback_advice(self, tracker: Tracker) -> str:
        """Generate helpful fallback when LLM fails"""
        interest = tracker.get_slot("career_interest") or "your field"
        major = tracker.get_slot("current_major") or "your major"
        
        return f"""
I'm having a brief technical hiccup, but let me share some general guidance about {interest}! 

For {major} in the UK, I'd recommend:  
**Immediate Steps:**
- Visit the university's career service (Career Space) for one-on-one guidance
- Explore opportunities on [Prospects](https://www.prospects.ac.uk) and [TargetJobs](https://www.TargetJobs.co.uk)
- Connect with alumni in {interest} via LinkedIn  

**Resources:**
- [Prospects Career Planner](https://www.prospects.ac.uk/)
- Visit the university's career service: [Career Space](https://www.wlv.ac.uk/current-students/careers-enterprise-and-the-workplace/career-space/)

Try asking me again in a moment, or let me know if you'd like to discuss something specific!
"""

    def _build_smart_conversation_history(self, tracker: Tracker, max_conversation_turns : int = 5, expire_after_user_messages: int = 20) -> str:
        """
        Build conversation history with:
        - max_conversation_turns: Maximum number of message turns (user + bot) to include
        - expire_after_user_messages: Number of user messages before advice expires

        1 conversation turn  = 1 user message + 1 bot message
        
        Example: max_conversation_turns=10 means 20 individual messages (could be 10 user + 10 bot)
        Example: expire_after_user_messages=20 means advice expires after 20 user inputs
        """

        logger.info("Building smart conversation history... \n\n")
        messages = []
        last_advice_timestamp = None

        # Extract messages and track when last advice was given
        for event in tracker.events:
            logger.debug(f"Processing event: {event} \n")
            event_type = event.get('event')

            # Only consider user and bot messages
            if event_type in ['user', 'bot']:
                logger.debug(f"Adding {event_type} message to history. \n")
                text = event.get('text', '')
                timestamp = event.get('timestamp', 0)

                if text:
                    messages.append({
                        'role': 'User' if event_type == 'user' else 'Assistant',
                        'text': text,
                        'timestamp': timestamp,
                        # 'timestamp': event.get('timestamp', 0),
                    })

                    # Track when advice action was called
                    if event_type == 'bot':
                        logger.debug("Checking for last career advice in bot message... \n")
                        last_full_advice = tracker.get_slot("last_career_advice_full")
                        if last_full_advice and text == last_full_advice:
                            last_advice_timestamp = timestamp


        # Sort by timestamp and take last N messages
        max_messages = max_conversation_turns * 2  # i.e. Each turn = user + bot
        messages.sort(key=lambda x: x['timestamp'])
        recent = messages[-max_messages:]

        # Check if advice has expired (too many turns ago)
        advice_expired = False
        if last_advice_timestamp:
            user_turns_since_advice = len([
                m for m in messages 
                if m['timestamp'] > last_advice_timestamp and m['role'] == 'User'
            ])
            advice_expired = user_turns_since_advice > expire_after_user_messages


        # Find last bot message in recent history
        last_bot_idx = None
        for i in range(len(recent) - 1, -1, -1):
            if recent[i]['role'] == 'Assistant':
                last_bot_idx = i
                break

        # Format recent messages with truncation
        formatted = []
        for i, msg in enumerate(recent):
            text = msg['text']

            # Truncate old bot messages (except the last one)
            if msg['role'] == 'Assistant' and i != last_bot_idx and len(text) > 100:
                text = text[:20] + "..."

            formatted.append(f"{msg['role']}: {text}")

        recent_history = "\n".join(formatted)

        # APPEND LAST FULL ADVICE: if it's not already in recent history
        last_full_advice = tracker.get_slot("last_career_advice_full")

        if last_full_advice and last_full_advice != "Fallback advice provided" and not advice_expired:
            # Check if this advice is already in the recent history (avoid duplication)
            last_bot_message = recent[last_bot_idx]['text'] if last_bot_idx is not None else ""

            # Only append if the stored advice is different from the last bot message
            if last_full_advice != last_bot_message:
                formatted.append(f"\n--- Previous Career Advice (for context) ---")
                formatted.append(f"Assistant: {last_full_advice}")
                return "\n".join(formatted)

        return recent_history

    def run(self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]):

        logger.info("Starting Career Advice action... \n")

        # full advice generation with context

        # Check if this is a correction scenario
        latest_message = tracker.latest_message.get('text', '').lower()
        correction_phrases = ["actually", "i meant", "sorry", "correction", "change that", "i said"]
        is_correction = any(phrase in latest_message for phrase in correction_phrases)

        # # Extract conversation history
        # user_messages = [
        #     event.get('text') 
        #     for event in tracker.events 
        #     if event.get('event') == 'user' and event.get('text')
        # ]
        # conversation_history = "\n".join([f"User: {msg}" for msg in user_messages[-5:]])

        # SMART HISTORY EXTRACTION: Extract recent conversation + preserved last advice
        conversation_history = self._build_smart_conversation_history(tracker, max_conversation_turns=3, expire_after_user_messages=5)

        # Get student profile
        student_name = tracker.get_slot("student_name") or "the student"
        major = tracker.get_slot("current_major") or "not specified"
        year = tracker.get_slot("year_of_study") or "not specified"
        interest = tracker.get_slot("career_interest") or "not specified"

        # Handle missing career interest
        if not interest or interest == "not specified":
            logger.info("Career interest missing; asking for clarification... \n")
            # Ask for clarification naturally
            dispatcher.utter_message(
                response="utter_clarify_interest"
            )
            logger.info("Prompted user to clarify career interest; setting needs_interest_clarification slot to True... \n")
            return [SlotSet("needs_interest_clarification", True)]

        gpa = tracker.get_slot("gpa") or "not provided"
        has_internship = tracker.get_slot("has_internship")
        internship_status = "Yes" if has_internship else "No" if has_internship is False else "not specified"
        visa_status = tracker.get_slot("visa_status") or "not specified"

        # # Get previous advice for follow-up context
        # last_advice = tracker.get_slot("last_career_summary") or "No previous advice given yet."

        # Get latest user message for context
        # user_query = tracker.get_slot("user_query") or ""
        latest_user_message = tracker.latest_message.get('text', '')

        # acknowledge corrections first
        if is_correction:
            dispatcher.utter_message(
                response="utter_correction_acknowledged"
            )

        user_prompt = f"""
## Student Profile (for grounding advice)
- Name: {student_name}
- Current Major: {major}
- Year of Study: {year}
- Career Interest: {interest}
- GPA/Classification Target: {gpa}
- Internship Experience: {internship_status}
- Visa Status: {visa_status}

## Conversation History (for full context)
{conversation_history}

## Emotional Context Detection
Analyze the student's latest message for emotional cues (Anxiety, Confusion, Excitement, etc.). If detected, acknowledge them empathetically *before* providing advice.

## Student's Latest Message:
{latest_user_message}

## Your Task (Synthesis and Response)
Based on the full history and the latest message, synthesize the student's core intent (initial query, follow-up, or correction). Generate the tailored career advice response now, ensuring it meets all the structural and quality standards set in the System Instructions.

4. **Include "Your Next Steps"** - Bulleted list of 2-3 concrete actions
5. **End with PROACTIVE SUGGESTIONS** - Based on their profile (Major, Year, Interest), suggest 2-3 related topics they might want to explore next to encourage continued planning. Format as a separate, bolded list:

**You might also want to explore:**
- [Topic 1 based on their major/interest]
- [Topic 2 based on their year]
- [Topic 3 based on their situation]
"""

        logger.info(f"""Student profile :
                    - Name: {student_name}
                    - Major: {major}
                    - Year: {year}
                    - Interest: {interest}
                    - GPA: {gpa}
                    - Internship: {internship_status}
                    - Visa: {visa_status} \n
                    """)

        logger.info(f"Is correction scenario? : {is_correction} \n")

        logger.info(f"Conversation history : \n{conversation_history} \n")

        # logger.info(f"last_career_summary slot content: {last_advice[:50]} \n")

        logger.info(f"Latest user message : {latest_user_message} \n")

        # logger.info(f"Final user prompt to Gemini : {user_prompt}\n")

        try:
            advice_response = self.safe_generate(
                model="gemini-2.5-flash", 
                user_prompt=user_prompt, 
                use_system_prompt=True
            )

            if advice_response:
                # SUCCESS: Log, send message, and return advice slot
                logger.info(f"Career advice generated successfully: {advice_response}...")

                # Use ONE utter_message call
                dispatcher.utter_message(text=advice_response)

                return [
                    SlotSet("last_career_summary", advice_response),
                    SlotSet("last_career_advice_full", advice_response),
                ]

            else:
               # FAILURE: Log the error and provide fallback advice.
                logger.warning("Gemini API returned None. Using fallback advice.")
                fallback_message = self._generate_fallback_advice(tracker)
                dispatcher.utter_message(text=fallback_message)

                # CRITICAL: Return a slot even on fallback to signal completion
                return [
                    SlotSet("last_career_summary", "Fallback advice was provided"),
                    SlotSet("last_career_advice_full", "Fallback advice was provided"),
                ]


        except Exception as e:
            # EXCEPTION: Log and provide fallback
            logger.error(f"Exception during career advice generation: {e}")
            fallback_message = self._generate_fallback_advice(tracker)
            dispatcher.utter_message(text=fallback_message)
            
            # CRITICAL: Return a slot to signal action completed
            return [
                    SlotSet("last_career_summary", "Fallback advice was provided"),
                    SlotSet("last_career_advice_full", "Fallback advice was provided"),
                ]



# Custom actions *must always* return events to signal completion to Rasa's dialogue manager
# even if an error occurs internally.
# Returning empty lists will break this contract.

