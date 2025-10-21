# from typing import Any, Text, Dict, List
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

# # Import the Google GenAI SDK
# from google import genai
# import os



# # --- INITIALIZE GEMINI CLIENT ---
# # This client will use the GEMINI_API_KEY environment variable.
# try:
#     # Use the specific model you defined in endpoints.yml
#     GEMINI_MODEL = "gemini-2.5-flash"
#     client = genai.Client()
# except Exception as e:
#     # Handle case where API key might be missing
#     print(f"Error initializing Gemini client: {e}")
#     client = None

# class ActionFindAdvisorContact(Action):
#     def name(self) -> Text:
#         return "action_find_advisor_contact"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:

#         # 1. Check if the client initialized successfully
#         if not client:
#             dispatcher.utter_message(text="I'm sorry, I cannot connect to the contact database right now.")
#             return []
            
#         # 2. Get the original user query for context
#         topic = tracker.get_slot("user_query")
        
#         # 3. Construct a specific search query for the LLM
#         if topic and len(topic.strip()) > 5:
#             search_query = f"Contact information for an academic advisor related to: {topic}"
#         else:
#             search_query = "General academic support advisor contact information"

#         # 4. Load the knowledge base file (your RAG documents)
#         try:
#             # NOTE: Update this path if actions server isn't running from the root Rasa directory
#             kb_path = os.path.join(os.getcwd(), 'docs', 'advisor_contacts.txt')
#             with open(kb_path, "r", encoding="utf-8") as f:
#                 knowledge_base = f.read()
#         except FileNotFoundError:
#             dispatcher.utter_message(text="I'm sorry, I couldn't access the specific advisor contact list.")
#             return []

#         # 5. Create a prompt for the LLM
#         prompt = f"""
#         You are a helpful and professional university assistant. 
#         Your task is to answer the user's QUERY using ONLY the provided CONTACT_DOCUMENT.
        
#         CONTACT_DOCUMENT:
#         ---
#         {knowledge_base}
#         ---

#         QUERY: {search_query}

#         Provide a concise answer. If a specific contact is found (e.g., Computer Science), prioritize it. If no match is found, clearly provide the 'General Academic Support' contact details.
#         """

#         # 6. Call the Gemini API for generation
#         try:
#             response = client.models.generate_content(
#                 model=GEMINI_MODEL,
#                 contents=prompt
#             )
#             llm_answer = response.text
            
#             # 7. Dispatch the LLM's answer
#             dispatcher.utter_message(text=llm_answer)

#         except Exception:
#             # Fallback if the API call fails
#             fallback_message = "I had trouble retrieving the specific contact, but you can always reach out to the General Academic Support at **student.support@university.edu**."
#             dispatcher.utter_message(text=fallback_message)
            
#         return []