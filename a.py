import os
import asyncio
from typing import Any, Text, Dict, List

from ddgs import DDGS
import google.generativeai as genai

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from .logger_utils import get_logger

# Initialize the logger function
logger = get_logger("CareerAdviceAction")


class ActionGiveCareerAdvice(Action):
    """
    Provides UK-focused career advice by:
      1. Searching DuckDuckGo for relevant results
      2. Using Gemini to generate personalized advice
      3. Returning structured guidance with sources
    """

    def name(self) -> Text:
        return "action_give_career_advice"
    
    @staticmethod
    def _validate_api_key() -> str:
        """Validate and return the Gemini API key."""
        api_key = os.getenv("GEMS")
        if not api_key:
            logger.critical("GEMS environment variable not set - Gemini API key missing")
            raise ValueError("Environment variable GEMS (Gemini API key) is missing")
        logger.debug("Gemini API key validation successful")
        return api_key

    @staticmethod
    def _search_ddgs(query: str) -> tuple[list[str], list[str]]:
        """
        Execute DuckDuckGo search and return snippets and sources.
        
        Returns:
            Tuple of (snippets, sources) lists
            
        Raises:
            ValueError: If no search results found
        """
        try:
            logger.info(f"Executing DuckDuckGo search with query: '{query}'")
            results = list(
                DDGS().text(
                    query,
                    max_results=8,
                    region="uk-en",
                    safesearch="moderate",
                )
            )
            
            snippets = [r.get("body") for r in results[:5] if r.get("body")]
            sources = [r.get("href") for r in results[:5] if r.get("href")]
            
            if not snippets:
                logger.warning(f"No snippets found for query: '{query}' - {len(results)} total results")
                raise ValueError("No relevant search results found")
                
            logger.info(f"Search successful: found {len(snippets)} snippets and {len(sources)} sources")
            return snippets, sources
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed for query '{query}': {str(e)}", exc_info=True)
            raise

    @staticmethod
    def _call_gemini(prompt: str, api_key: str) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            prompt: The prompt to send to Gemini
            api_key: Gemini API key
            
        Returns:
            Generated text response
        """
        try:
            logger.debug("Configuring Gemini API client")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            logger.info("Sending prompt to Gemini API (approx length: %d chars)", len(prompt))
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    max_output_tokens=500,
                ),
            )
            
            logger.debug("Gemini API response received successfully")
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}", exc_info=True)
            raise

    def _build_search_query(
        self,
        interest: str,
        major: str,
        year: str,
        has_internship: bool,
    ) -> str:
        """Construct UK-focused search query."""
        internship_text = (
            "with internship experience" if has_internship else "entry-level"
        )
        query = (
            f"2025 {interest} career advice {major} {year} student {internship_text} "
            f"site:.ac.uk OR site:.gov.uk OR site:linkedin.com/company/uk- OR site:indeed.co.uk"
        )
        logger.debug(f"Built search query: '{query}'")
        return query

    def _build_gemini_prompt(
        self,
        year: str,
        major: str,
        gpa: str,
        interest: str,
        has_internship: bool,
        snippets: list[str],
    ) -> str:
        """Construct prompt for Gemini API."""
        internship_status = (
            "They have internship experience."
            if has_internship
            else "They are looking for entry-level opportunities."
        )
        
        prompt = f"""You are a warm, encouraging career counsellor at the University of Wolverhampton.
A {year} {major} student (GPA {gpa}) is asking for advice about {interest}.
{internship_status}

Using ONLY the following UK-focused search results, write 4-5 upbeat bullet points:
- Simple, friendly language with 1-2 emojis per point
- Highlight 2025 job prospects, must-have skills, internship ideas, and CV/LinkedIn tips for the UK market
- End with a short networking suggestion (e.g., LinkedIn groups, university alumni events)

Search results:
{chr(10).join(snippets)}

Advice:
"""
        logger.debug(f"Built Gemini prompt with {len(snippets)} snippets, total length: {len(prompt)} chars")
        return prompt

    def _get_fallback_advice(self, interest: str) -> tuple[str, str]:
        """Return fallback advice when external services fail."""
        logger.warning(f"Generating fallback advice for interest: {interest}")
        advice = f"""Sorry, I couldn't fetch fresh web data right now. Here's solid, UK-focused guidance for {interest}:

• **2025 Trends** – Look for roles in cybersecurity, AI, data science, and cloud engineering 🚀
• **Key Skills** – Strengthen Python, cloud (AWS/Azure), and data-visualisation (Power BI/Tableau) 📚
• **Experience** – Try personal projects, open-source contributions, or volunteer work 💼
• **Networking** – Join LinkedIn UK groups, attend the University of Wolverhampton Careers Fair, and connect with alumni 🤝

The University's Careers Service can give you personalised advice! 🎓"""
        
        sources = "General UK resources: National Careers Service, Prospects, LinkedIn Learning"
        return advice, sources

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """Execute the career advice action."""
        
        # Log action execution start with user context
        logger.info(f"Starting career advice action for user: {tracker.sender_id}")
        
        # Validate API key early
        try:
            api_key = self._validate_api_key()
        except ValueError as e:
            # Critical error - configuration issue that needs immediate attention
            logger.critical(f"API key validation failed: {str(e)}")
            dispatcher.utter_message(
                text="I'm having configuration issues. Please contact support."
            )
            return [SlotSet("config_error", True)]

        # Extract and normalize slot values with debug logging
        major = tracker.get_slot("current_major") or "your field of study"
        interest = tracker.get_slot("career_interest") or "career path"
        year = tracker.get_slot("year_of_study") or "current year"
        gpa = tracker.get_slot("gpa") or "N/A"
        
        has_internship_slot = tracker.get_slot("has_internship")
        has_internship = (
            str(has_internship_slot).lower() in ["true", "yes", "1", "y"]
            if has_internship_slot is not None
            else False
        )
        
        logger.debug(f"Extracted slots - major: {major}, interest: {interest}, year: {year}, "
                    f"GPA: {gpa}, has_internship: {has_internship}")

        # Build search query
        query = self._build_search_query(interest, major, year, has_internship)

        # Execute search in thread pool
        try:
            snippets, sources = await asyncio.to_thread(self._search_ddgs, query)
        except Exception as e:
            # Search failed - use fallback but don't crash the action
            logger.warning(f"Search failed for user {tracker.sender_id}, using fallback: {str(e)}")
            advice_text, sources_list = self._get_fallback_advice(interest)
            dispatcher.utter_message(text=advice_text)
            dispatcher.utter_message(text=f"Sources:\n{sources_list}")
            dispatcher.utter_message(text="Anything else I can help you with?")
            
            # Log successful fallback completion
            logger.info(f"Fallback advice delivered successfully for user: {tracker.sender_id}")
            return []

        # Build prompt and call Gemini
        prompt = self._build_gemini_prompt(
            year, major, gpa, interest, has_internship, snippets
        )
        
        try:
            advice_text = await asyncio.to_thread(
                self._call_gemini, prompt, api_key
            )
        except Exception as e:
            # Gemini API failed - use fallback
            logger.error(f"Gemini API call failed for user {tracker.sender_id}: {str(e)}")
            advice_text, sources_list = self._get_fallback_advice(interest)
            dispatcher.utter_message(text=advice_text)
            dispatcher.utter_message(text=f"Sources:\n{sources_list}")
            dispatcher.utter_message(
                text="Let me know if you'd like more details on any point."
            )
            
            logger.info(f"Fallback advice delivered after Gemini failure for user: {tracker.sender_id}")
            return []

        # Format and send successful response 
        sources_list = "\n".join([f"• {src}" for src in sources if src])
        
        dispatcher.utter_message(text=advice_text)
        dispatcher.utter_message(text=f"Sources for this advice:\n{sources_list}")
        dispatcher.utter_message(
            text="Hope that helps! Feel free to ask for more detail on any point or about other career options."
        )

        # Log successful completion
        logger.info(f"Career advice successfully delivered for user: {tracker.sender_id}, "
                   f"interest: {interest}, major: {major}")
        
        # Clear any previous config error slot if this succeeded
        return [SlotSet("config_error", None)]