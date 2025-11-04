import os
from typing import Any, Text, Dict, List
from ddgs import DDGS  # pip install ddgs
import google.generativeai as genai
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionGiveCareerAdvice(Action):
    def name(self) -> Text:
        return "action_give_career_advice"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        major = tracker.get_slot("current_major") or "your major"
        interest = tracker.get_slot("career_interest") or "careers"
        year = tracker.get_slot("year_of_study") or "your year"
        gpa = tracker.get_slot("gpa")
        gpa = gpa if gpa is not None else "N/A"
        has_internship = tracker.get_slot("has_internship")
        has_internship = str(has_internship).lower() == "true"

        query = (
            f"2025 {interest} career advice {major} {year} student {gpa} GPA "
            f"{'with internship experience' if has_internship else 'entry-level'} "
            "site:edu OR site:gov OR site:linkedin.com OR site:indeed.com"
        )

        try:
            results = list(DDGS().text(query, max_results=10))
            snippets, sources = [], []
            for result in results[:5]:
                snippets.append(result.get("body", ""))
                sources.append(result.get("href", ""))
            sources_list = ", ".join([f"[{i+1}] {src}" for i, src in enumerate(sources) if src])
            
            # Compose the prompt
            prompt = (
                f"You are a warm, encouraging university career counselor. Summarize these search results into 4-5 upbeat bullet points of advice for a {year} {major} student (GPA {gpa}) interested in {interest} "
                f"({'with internship experience' if has_internship else 'entry-level'}). "
                "Use simple language, add 1-2 emojis per point. Focus on 2025 jobs, skills, internships, and resume tips. "
                "Base ONLY on these snippets—no external knowledge. End with a networking nudge.\n\n"
                f"Snippets:\n{chr(10).join(snippets)}"
            ) # note: chr(10) <==> '\n'

            GEM_API_KEY = os.getenv("GEMS")
            genai.configure(api_key=GEM_API_KEY)

            model = genai.GenerativeModel('Gemini-2.5-flash')

            response = model.generate_content(prompt)

            advice_text = response.text
            
            # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            # response = client.chat.completions.create(
            #     model="gpt-4o-mini",
            #     messages=[{"role": "user", "content": prompt}],
            #     temperature=0.3,
            #     max_tokens=300
            # )
            # advice_text = response.choices[0].message.content.strip()

        except Exception as e:
            advice_text = (
                f"Sometimes pulling fresh web info hits a snag—here's solid, timeless guidance for {interest} in {major}:\n"
                "- **Hot 2025 roles:** Think data analyst or dev roles—demand's skyrocketing! 🚀\n"
                "- **Key skills:** Dive into Python/SQL via free online bootcamps.\n"
                "- **Internship hunt:** Hit up Handshake or LinkedIn for summer gigs; apply early.\n"
                "- **Resume hack:** Use numbers, like 'Boosted project efficiency by 30%.'\n"
                "Start connecting on LinkedIn today—you're already ahead! 💪"
            )
            sources_list = "Fallback: Timeless resources like your university career center or BLS.gov."
            print(f"[action_give_career_advice] Error: {e}")

        # Deliver the response with rephrase metadata enabled on utterances
        dispatcher.utter_message(
            response="utter_advice_core",
            advice_text=advice_text,
            current_major=major,
            career_interest=interest,
            year_of_study=year,
        )
        dispatcher.utter_message(response="utter_encourage_human")
        dispatcher.utter_message(
            response="utter_cite_sources",
            sources_list=sources_list
        )
        return []
