# import os
# import sys
# import asyncio
# from typing import Any, Text, Dict, List

# from ddgs import DDGS         # sync library
# from google import genai      # sync library

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

# from actions.general.logger_utils import get_logger


# # Initialize a logger for this global setup block
# logger = get_logger(__name__)


# class ActionGiveCareerAdvice(Action):
#     """
#     Async Rasa action that:
#       1. Builds a UK‑focused DuckDuckGo query
#       2. Retrieves the top 5 snippets (run in a thread)
#       3. Sends those snippets to Gemini‑Pro (also run in a thread)
#       4. Returns bullet‑point advice + sources
#     """

#     def name(self) -> Text:
#         return "action_give_career_advice"

#     # ---------------------------------------------------------
#     # Helper – run the **blocking** DDGS search in a thread
#     # ---------------------------------------------------------
#     @staticmethod
#     def _search_ddgs(query: str) -> tuple[list[str], list[str]]:
#         """
#         Returns (snippets, sources).  Raises if no results.
#         """
#         results = list(
#             DDGS().text(
#                 query,
#                 max_results=8,
#                 region="uk-en",          # bias toward the United Kindom
#                 safesearch="moderate",
#             )
#         )

#         snippets, sources = [], []
#         for result in results[:5]:          # keep only the 5 most relevant
#             body = result.get("body")
#             href = result.get("href")
            
#             if body:
#                 snippets.append(body)
            
#             if href:
#                 sources.append(href)

#         if not snippets:
#             raise ValueError("No relevant search results found.")
#             ## TODO: Use logger or slot events to handle this error!
#             logger.error("_search_ddgs: No relevant search results found!")
#         return snippets, sources

#     # ---------------------------------------------------------
#     # Helper – call Gemini in a thread
#     # ---------------------------------------------------------
#     @staticmethod
#     def _call_gemini(prompt: str, api_key: str) -> str:
#         genai.configure(api_key=api_key)

#         # You can swap model names – `gemini-pro` gives higher quality than flash
#         model = genai.GenerativeModel("gemini-pro")

#         response = model.generate_content(
#             prompt,
#             generation_config=genai.types.GenerationConfig(
#                 temperature=0.7,
#                 top_p=0.8,
#                 max_output_tokens=500,
#             ),
#         )
#         return response.text.strip()

#     # ---------------------------------------------------------
#     # Async entry point
#     # ---------------------------------------------------------
#     async def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
        
#         # -----------------------------------------------------------------
#         # Call Gemini in a thread (again non‑blocking)
#         # -----------------------------------------------------------------
#         # Check for env var early, fail fast
#         GEM_API_KEY = os.getenv("GEM_SP_KEY")
#         if not GEM_API_KEY:
#             logger.error("Gemini API key [GEM_API_KEY] missing.")
#             # return [SlotSet("config_error", True)]

#         # -----------------------------------------------------------------
#         # Pull slots (no async work needed here)
#         # -----------------------------------------------------------------
#         major = tracker.get_slot("current_major") or "your field of study"
#         interest = tracker.get_slot("career_interest") or "career path"
#         year = tracker.get_slot("year_of_study") or "current year"
#         gpa = tracker.get_slot("gpa") or "N/A"

#         # Normalise the internship flag
#         has_internship_slot = tracker.get_slot("has_internship")
#         has_internship = (
#             str(has_internship_slot).lower() in ["true", "yes", "1", "y"]
#             if has_internship_slot is not None
#             else False
#         )

#         # -----------------------------------------------------------------
#         # Build a UK‑specific query
#         # -----------------------------------------------------------------
#         query = (
#             f"2025 {interest} career advice {major} {year} student "
#             f"{'with internship experience' if has_internship else 'entry-level'} "
#             f"site:.ac.uk OR site:.gov.uk OR site:linkedin.com/company/uk- OR site:indeed.co.uk"
#         )

#         # -----------------------------------------------------------------
#         # Async operation: Run the *blocking* search in a thread (non‑blocking for Rasa)
#         # -----------------------------------------------------------------
#         try:
#             snippets, sources = await asyncio.to_thread(self._search_ddgs, query)
#         except Exception as e:
#             # ---------- Fallback when the web search fails ----------
#             advice_text = f"""
# Sorry, I couldn’t fetch fresh web data right now. Here’s solid, UK‑focused guidance for {interest}:

# • **2025 Trends** – Look for roles in cybersecurity, AI, data science, and cloud engineering 🚀
# • **Key Skills** – Strengthen Python, cloud (AWS/Azure), and data‑visualisation (Power BI/Tableau) 📚
# • **Experience** – Try personal projects, open‑source contributions, or volunteer work 💼
# • **Networking** – Join LinkedIn UK groups, attend the University of Wolverhampton Careers Fair, and connect with alumni 🤝

# The University’s Careers Service can give you personalised advice! 🎓
# """
#             sources_list = "General UK resources: National Careers Service, Prospects, LinkedIn Learning"
#             # Send the fallback and exit early
#             dispatcher.utter_message(text=advice_text)
#             dispatcher.utter_message(text=f"Sources:\n{sources_list}")
#             dispatcher.utter_message(text="Anything else I can help you with?")
#             return [SlotSet("last_career_summary", advice_text)]

#         # -----------------------------------------------------------------
#         # Build the *prompt* that will be fed to Gemini
#         # -----------------------------------------------------------------
        
#         prompt = f"""
# You are a warm, encouraging career counsellor at the University of Wolverhampton.
# A {year} {major} student (GPA {gpa}) is asking for advice about {interest}.
# {'They have internship experience.' if has_internship else 'They are looking for entry‑level opportunities.'}

# Using ONLY the following UK‑focused search results, write 4‑5 upbeat bullet points:
# - Simple, friendly language with 1‑2 emojis per point
# - Highlight 2025 job prospects, must‑have skills, internship ideas, and CV/LinkedIn tips for the UK market
# - End with a short networking suggestion (e.g., LinkedIn groups, university alumni events)

# Search results:
# {chr(10).join(snippets)}

# Advice:
# """     
#         try:
#             advice_text = await asyncio.to_thread(
#                 self._call_gemini, prompt, GEM_API_KEY
#             )
#         except Exception as e:
#             # ---------- Gemini failure fallback ----------
#             advice_text = f"""
# I ran into a problem while generating the answer. Here’s a quick, timeless UK‑focused tip for {interest}:

# • Focus on building Python, cloud, and data‑analysis skills.
# • Look for graduate schemes on Prospects, TargetJobs, and the university’s job board.
# • Start a small personal project and showcase it on GitHub/LinkedIn.

# The Careers Service at Wolverhampton can help you tailor this further! 🎓
# """
#             sources_list = "General UK resources: National Careers Service, Prospects, LinkedIn Learning"
#             dispatcher.utter_message(text=advice_text)
#             dispatcher.utter_message(text=f"Sources:\n{sources_list}")
#             dispatcher.utter_message(text="Let me know if you’d like more details on any point.")
#             return [SlotSet("last_career_summary", advice_text)]


#         # -----------------------------------------------------------------
#         # Prepare a tidy sources list for the user
#         # -----------------------------------------------------------------
#         sources_list = "\n".join([f"• {src}" for src in sources if src])

#         # -----------------------------------------------------------------
#         # Send everything back to the user – keep the conversation natural
#         # -----------------------------------------------------------------
#         # # a – the advice (the LLM output)
#         # dispatcher.utter_message(text=advice_text)

#         # # b – a short “here are the sources” line (optional, but nice for transparency)
#         # dispatcher.utter_message(text=f"Sources for this advice:\n{sources_list}")

#         # # c – a gentle follow‑up that encourages the user to keep chatting
#         # dispatcher.utter_message(
#         #     text="Hope that helps! Feel free to ask for more detail on any point or about other career options."
#         # )

#         ### OR: ###
#         full_message = f"{advice_text}\n\n**Sources:**\n{sources_list}\n\nHope that helps! Feel free to ask for more detail."
#         dispatcher.utter_message(text=full_message)

#         return [SlotSet("last_career_summary", advice_text)]   
#         # return [] # no events to set, just plain messages


# class ActionFollowupCareerAdvice(Action):
#     def name(self) -> str:
#         return "action_followup_career_advice"

#     async def run(self, dispatcher, tracker, domain):
#         last_summary = tracker.get_slot("last_career_summary")
#         followup = tracker.get_slot("followup_question")

#         if not last_summary:
#             dispatcher.utter_message(text="I don’t seem to have any previous advice stored. Could you tell me what you’d like to know?")
#             return []

#         prompt = f"""
#         The student previously received this advice:

#         {last_summary}

#         Now they’re asking: "{followup}"

#         Expand naturally on the earlier points, keeping the same tone and context.
#         """

#         # reuse Gemini from your existing helper
#         from .give_career_advice_b import ActionGiveCareerAdvice
#         try:
#             answer = await asyncio.to_thread(ActionGiveCareerAdvice._call_gemini, prompt, os.getenv("GEMS"))
#             dispatcher.utter_message(text=answer)
#         except Exception:
#             dispatcher.utter_message(text="Sorry, I couldn't expand on that just now. Try rephrasing your question?")
#         return []
