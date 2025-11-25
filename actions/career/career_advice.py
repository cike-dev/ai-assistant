# # Copyright 2024 Google LLC

# from typing import Any, Text, Dict, List

# import os
# # import asyncio
# from google import genai
# from google.genai import types
# # from IPython.display import Markdown

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet
# from actions.general.logger_utils import get_logger

# logger = get_logger(__name__)

# class ActionGiveCareerAdvice(Action):
#     def __init__(self) -> None:
#         super().__init__()
#         self.api_key = os.getenv("GEMINI_RAG_KEY")
#         if not self.api_key:
#             logger.error("GEMINI_RAG_KEY environment variable not set")
#         self.client = genai.Client(api_key=self.api_key)

#         self.NATURAL_CONVERSATION_PROMPT = """
# You are a warm, encouraging career counsellor at the University of Wolverhampton. You're having a friendly conversation with a student.

# Speak naturally like a human advisor:
# - Use conversational language with occasional emojis to show warmth 😊
# - Vary your response style - sometimes use short paragraphs, sometimes brief lists, but always flow naturally
# - Share personal insights and practical tips like you would in a real conversation
# - Show empathy and understanding of their situation
# - Focus on UK-specific job market trends for 2025
# - Mention specific skills, internship opportunities, and UK resources
# - Keep it practical and actionable
# - End with an encouraging note and invite them to ask more questions

# Remember: You're talking to a student, not writing a formal report. Be supportive and relatable!
# """

#     def name(self) -> Text:
#         return "action_give_career_advice"

#     def add_citations(self, response):
#         """Safely add citations to response text with proper error handling"""
#         if not response or not response.candidates:
#             return response.text if response and hasattr(response, 'text') else "No response generated"
        
#         text = response.text
        
#         # Check if grounding metadata exists
#         if (not hasattr(response.candidates[0], 'grounding_metadata') or 
#             not response.candidates[0].grounding_metadata):
#             return text
        
#         grounding_metadata = response.candidates[0].grounding_metadata
#         supports = grounding_metadata.grounding_supports
#         chunks = grounding_metadata.grounding_chunks

#         if not supports or not chunks:
#             return text

#         # Sort supports by end_index in descending order
#         sorted_supports = sorted(supports, key=lambda s: s.segment.end_index, reverse=True)

#         for support in sorted_supports:
#             end_index = support.segment.end_index
#             if support.grounding_chunk_indices:
#                 citation_links = []
#                 for i in support.grounding_chunk_indices:
#                     if i < len(chunks) and hasattr(chunks[i], 'web') and chunks[i].web.uri:
#                         uri = chunks[i].web.uri
#                         citation_links.append(f"[{i + 1}]({uri})")

#                 if citation_links:
#                     citation_string = ", ".join(citation_links)
#                     text = text[:end_index] + " " + citation_string + text[end_index:]

#         return text

#     # async def run(
#     #     self,
#     #     dispatcher: CollectingDispatcher,
#     #     tracker: Tracker,
#     #     domain: Dict[Text, Any],
#     # ) -> List[Dict[Text, Any]]:
#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         logger.info("Starting career advice action... \n")

#         # Pull slots
#         major = tracker.get_slot("current_major") or "your field of study"
#         interest = tracker.get_slot("career_interest") or "career path"
#         year = tracker.get_slot("year_of_study") or "current year"
#         gpa = tracker.get_slot("gpa") or "N/A"

#         # Normalise internship flag
#         has_internship_slot = tracker.get_slot("has_internship")
#         has_internship = (
#             str(has_internship_slot).lower() in ["true", "yes", "1", "y"]
#             if has_internship_slot is not None
#             else False
#         )

#         logger.debug(f"Student major: {major}, interest: {interest}, year: {year}, GPA: {gpa}, has_internship: {has_internship} \n")

#         USER_PROMPT = f"""
# I'm a {year} {major} student with a GPA of {gpa}, and I'm really interested in {interest}. 
# {'I have some internship experience which was really helpful.' if has_internship else "I'm looking to get started and find entry-level opportunities."}

# Could you give me some friendly advice about pursuing this career in the UK? I'd love to hear what opportunities are out there and how I can prepare.
# """
  
#         try:
#             grounding_tool = types.Tool(
#                 google_search=types.GoogleSearch()
#             )

#             config = types.GenerateContentConfig(
#                 tools=[grounding_tool],
#                 temperature=0.7,
#                 top_p=0.8,
#                 max_output_tokens=1000,
#                 system_instruction=self.NATURAL_CONVERSATION_PROMPT
#             )

#             logger.info("Sending career advice prompt to Gemini API... \n")

#             # CORRECT ASYNC METHOD - Using the proper async API
#             # response = await self.client.aio.models.generate_content(
#             response = self.client.models.generate_content(
#                 model="gemini-2.5-flash",  # or "gemini-2.0-flash" depending on availability
#                 contents=USER_PROMPT,
#                 config=config,
#             )

#             logger.info("Career advice response received.\n")

#             if response and response.text:
#                 advice_with_citations = self.add_citations(response)
#                 full_message = f"{advice_with_citations}\n\nHope that helps! Feel free to ask for more detail."
#                 dispatcher.utter_message(text=full_message)
#                 logger.info("Career advice sent to user:=> %s... \n", full_message[:15])

#                 # Update advice_history slot
#                 advice_history = tracker.get_slot("advice_history") or []
#                 if not isinstance(advice_history, list):
#                     advice_history = [advice_history] if advice_history else []
#                 updated_history = advice_history + [response.text]
#                 # updated_history = advice_history + [response.text.strip()]

#                 logger.info("Updated advice history:=> %s... \n", updated_history[-1][:15])
#                 logger.debug(f"Full advice history now has {len(updated_history)} entries. \n")
                
#                 return [
#                     SlotSet("last_career_summary", response.text),
#                     # SlotSet("last_career_summary", response.text.strip()),
#                     SlotSet("advice_history", updated_history)
#                 ]

#         except Exception as e:
#             logger.error(f"Gemini API error: {e}")

#             # response_template = domain["responses"]["utter_falllback_advice"][0]["text"]
#             # dispatcher.utter_message(text=response_template)
#             response_template = (
#                f"I'm having trouble accessing the latest career data right now, but let me share some general thoughts about {interest} in the UK market! 😊"

#                 "Many students find that building strong Python and cloud skills really opens doors here. The UK tech scene is growing fast, and there are some great graduate schemes on platforms like TargetJobs and Prospects."

#                 "Have you had a chance to explore the university's Careers Service? They offer fantastic one-on-one guidance tailored specifically to Wolverhampton students!"

#                 f"What aspects of {interest} are you most curious about?"
#             )
#             dispatcher.utter_message(template="utter_fallback_advice")
#             logger.info("Sent fallback career advice message: '%s...' \n", response_template[:30])
            
#             advice_history = tracker.get_slot("advice_history") or []
#             if not isinstance(advice_history, list):
#                 advice_history = [advice_history] if advice_history else []
#             updated_history = advice_history + [response_template]

#             logger.info("Updated advice history with fallback:=> %s... \n", updated_history[-1][:15])

#             return [
#                 SlotSet("last_career_summary", response_template),
#                 SlotSet("advice_history", updated_history)
#             ]



# # -------------------------------------------
# # Follow-up career advice action
# # -------------------------------------------
# class ActionFollowupCareerAdvice(Action):
#     def __init__(self) -> None:
#         super().__init__()
#         self.api_key = os.getenv("GEMINI_SEARCH_GROUNDING")
#         self.client = genai.Client(api_key=self.api_key) if self.api_key else None

#     def name(self) -> str:
#         return "action_followup_career_advice"

#     # async def run(self,
#     #     dispatcher: CollectingDispatcher,
#     #     tracker: Tracker,
#     #     domain: Dict[Text, Any],
#     # ) -> List[Dict[Text, Any]]:
    
#     # async def run(self, dispatcher, tracker, domain):
#     def run(self, dispatcher, tracker, domain):
        
#         logger.info("Starting follow-up career advice action... \n")

#         history = tracker.get_slot("advice_history") or []
#         last_summary = tracker.get_slot("last_career_summary")
#         followup = tracker.get_slot("followup_question")

#         logger.debug(f"Advice history: {len(history)} entries \n")
#         logger.debug(f"Last career summary: {last_summary[:15] if last_summary else 'None'} \n")

#         if not last_summary:
#             dispatcher.utter_message(text="I don't seem to have any previous advice stored. Could you tell me what you'd like to know?")
#             logger.debug("No last career summary found for follow-up. \n")
#             return []

#         prompt = f"""
# The student previously received this advice:

# {last_summary}

# Now they're asking: "{followup}"

# Expand naturally on the earlier points, keeping the same warm, encouraging tone and UK-focused context.

# This is the advice history so far:
# {history}
# """

#         if not self.client:
#             dispatcher.utter_message(text="Sorry, I'm having technical issues. Please try again later.")
#             logger.error("Gemini API key not set for follow-up action. \n")
#             return []

#         try:
#             grounding_tool = types.Tool(
#                 google_search=types.GoogleSearch()
#             )

#             config = types.GenerateContentConfig(
#                 tools=[grounding_tool],
#                 temperature=0.7,
#                 top_p=0.8,
#                 max_output_tokens=1000,
#             )

#             logger.info("Sending follow-up career advice prompt to Gemini API... \n")

#             # CORRECT ASYNC METHOD for follow-up
#             # response = await self.client.aio.models.generate_content(
#             response = self.client.models.generate_content(
#                 model="gemini-2.5-flash",
#                 contents=prompt,
#                 config=config,
#             )

#             logger.info("Follow-up career advice response received. \n")

#             # answer = response.text.strip()
#             answer = response.text
#             dispatcher.utter_message(text=answer)
#             logger.info("Sent follow-up career advice message:=> %s... \n", answer[:15])

#             # Fetch the existing advice history; default to an empty list if None.
#             advice_history = tracker.get_slot("advice_history") or []

#             # Ensure advice_history is a list (protect against accidental string values).
#             if not isinstance(advice_history, list):
#                 advice_history = [advice_history] if advice_history else []

#             # Append the new answer.
#             updated_history = advice_history + [answer]

#             # Optionally, set last_career_summary as well if you want.
#             return [
#                 SlotSet("advice_history", updated_history),
#                 SlotSet("last_career_summary", answer)
#             ]

#         except Exception as e:
#             logger.error(f"Followup career advice error: {e}")
#             dispatcher.utter_message(text="Sorry, I couldn't expand on that just now. Try rephrasing your question?")
#             logger.info("Sent fallback follow-up career advice message. \n")
#             return []