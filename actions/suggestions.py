# SYSTEM_INSTRUCTIONS = """You are a friendly, knowledgeable career advisor at a UK university, helping undergraduate students navigate their career paths.

# ## Your Core Responsibilities
# - Provide career guidance tailored to the **UK job market** and higher education system
# - Offer advice suitable for **undergraduate students** (typically ages 18-22)
# - Be warm, encouraging, and realistic about opportunities and challenges
# - **Seamlessly handle both initial queries and follow-up questions** in the same conversation

# ## UK-Specific Context
# - Reference UK job market trends, graduate schemes (e.g., Big 4, FMCG rotational programs), and recruitment cycles
# - Mention UK resources: Prospects, TargetJobs, RateMyPlacement, university careers services
# - Consider UK work visa requirements for international students (Graduate Route, Skilled Worker)
# - Reference UK qualifications: 2:1, 1st class degrees; professional bodies (CIPD, ACCA, BCS)
# - Acknowledge UK academic calendar: autumn term internship applications, spring assessment centers, summer placements

# ## Undergraduate-Appropriate Guidance
# - Assume limited work experience; focus on building foundational skills
# - Emphasize: internships, industrial placements, part-time work, volunteering, societies
# - Discuss: graduate schemes, entry-level roles, Masters programs, gap years
# - Address common concerns: CV building, LinkedIn presence, networking, imposter syndrome

# ## Advice Quality Standards (ALWAYS)
# ✓ **Relevant** - Directly address the student's query and situation
# ✓ **Timely** - Consider their year and upcoming deadlines (e.g., "As a penultimate year student, autumn internship applications open soon")
# ✓ **Actionable** - Provide concrete next steps they can take this week/month
# ✓ **Realistic** - Be honest about competitiveness while remaining encouraging
# ✓ **Encouraging** - Acknowledge strengths and frame challenges as growth opportunities

# ## Handling Follow-up Questions
# When the student asks a follow-up:
# 1. **Reference your previous advice** explicitly (e.g., "Building on what we discussed about CVs...")
# 2. **Go deeper** into the specific aspect they're curious about
# 3. **Maintain continuity** - don't repeat what you've already covered unless they ask
# 4. **Adjust recommendations** based on new information they share

# ## Response Structure
# 1. **Brief acknowledgment** of their question/concern (1 sentence)
# 2. **Tailored advice** addressing their specific situation (2-3 paragraphs, 100-200 words)
# 3. **"Your Next Steps"** - Bulleted list of 2-3 concrete actions
# 4. **UK Resources** - 1-2 relevant links or services
# 5. **Encouragement** - One supportive closing line

# **Tone:** Friendly but professional, like a supportive mentor. Use emojis sparingly (1-2 max). Keep responses concise unless depth is needed.
# """


# # ===== Suggested Career Advice Action =====
# from typing import Any, Text, Dict
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet
# import logging

# logger = logging.getLogger(__name__)

# SYSTEM_INSTRUCTIONS = """[Use the enhanced version above]"""

# class ActionGiveCareerAdvice(Action):
#     def name(self) -> Text:
#         return "action_give_career_advice"
    
#     def run(self, 
#             dispatcher: CollectingDispatcher, 
#             tracker: Tracker, 
#             domain: Dict[Text, Any]):
        
#         logger.info("Starting Career Advice action...")
        
#         # Check if this is a correction scenario
#         latest_message = tracker.latest_message.get('text', '').lower()
#         correction_phrases = ["actually", "i meant", "sorry", "correction", "change that", "i said"]
#         is_correction = any(phrase in latest_message for phrase in correction_phrases)
        
#         # Extract conversation history
#         user_messages = [
#             event.get('text') 
#             for event in tracker.events 
#             if event.get('event') == 'user' and event.get('text')
#         ]
#         conversation_history = "\n".join([f"User: {msg}" for msg in user_messages[-10:]])
        
#         # Get student profile
#         student_name = tracker.get_slot("student_name") or "the student"
#         major = tracker.get_slot("current_major") or "not specified"
#         year = tracker.get_slot("year_of_study") or "not specified"
#         interest = tracker.get_slot("career_interest") or "not specified"
#         gpa = tracker.get_slot("gpa") or "not provided"
#         has_internship = tracker.get_slot("has_internship")
#         internship_status = "Yes" if has_internship else "No" if has_internship is False else "not specified"
#         visa_status = tracker.get_slot("visa_status") or "not specified"
        
#         # Get previous advice
#         last_advice = tracker.get_slot("last_career_summary") or "No previous advice given yet."
        
#         # Get latest user message
#         latest_message_full = tracker.latest_message.get('text', '')
        
#         # If it's a correction, acknowledge it first
#         if is_correction:
#             dispatcher.utter_message(response="utter_correction_acknowledged")
        
#         user_prompt = f"""
# ## Student Profile (for grounding advice)
# - Name: {student_name}
# - Current Major: {major}
# - Year of Study: {year}
# - Career Interest: {interest}
# - GPA/Classification Target: {gpa}
# - Internship Experience: {internship_status}
# - Visa Status: {visa_status}

# ## Previous Advice Given
# {last_advice}

# ## Conversation History (last 10 messages)
# {conversation_history}

# ## Student's Latest Message
# {latest_message_full}

# ## Context
# {"The student is correcting previous information. Acknowledge the correction and adjust advice accordingly." if is_correction else ""}

# ## Your Task
# Based on the conversation history and latest message:

# 1. **IDENTIFY INTENT:** Determine if this is:
#    - An initial career question requiring comprehensive advice
#    - A follow-up seeking clarification or deeper detail
#    - A correction of previously provided information
#    - A goodbye/closing statement

# 2. **PROVIDE TAILORED RESPONSE:**
#    - If correction: Briefly acknowledge and provide updated advice
#    - If follow-up: Reference previous advice and go deeper
#    - If new question: Provide fresh guidance
#    - If goodbye: Provide a warm closing (this will be handled by the flow)

# 3. **Include "Your Next Steps"** - Bulleted list of 2-3 concrete actions

# 4. **Mention relevant UK resources**

# 5. **End with encouragement** - One supportive line

# Generate your career advice response now:
# """

#         # Call your LLM
#         try:
#             advice_response = self.generate_advice_with_llm(
#                 system_instructions=SYSTEM_INSTRUCTIONS,
#                 user_prompt=user_prompt
#             )
            
#             dispatcher.utter_message(text=advice_response)
            
#             return [
#                 SlotSet("last_career_summary", advice_response)
#             ]
            
#         except Exception as e:
#             logger.error(f"Error generating career advice: {e}")
#             dispatcher.utter_message(response="utter_fallback_advice")
#             return []
    
#     def generate_advice_with_llm(self, system_instructions: str, user_prompt: str) -> str:
#         """Call your LLM provider"""
#         pass  # Your implementation



# # ========== More suggestions ==========
# '''
# Improvement 4: Proactive Suggestions Based on Profile

# Problem: After giving advice, the bot waits passively. It could proactively suggest related topics.

# Solution: Update your action to include contextual suggestions.
# '''
# class ActionGiveCareerAdvice(Action):
#     def name(self) -> Text:
#         return "action_give_career_advice"
    
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
#         # ... [your existing code] ...
        
#         # Add proactive suggestions to the prompt
#         user_prompt = f"""
# ## Student Profile
# - Name: {student_name}
# - Current Major: {major}
# - Year of Study: {year}
# - Career Interest: {interest}
# - GPA: {gpa}
# - Internship Experience: {internship_status}
# - Visa Status: {visa_status}

# ## Previous Advice Given
# {last_advice}

# ## Conversation History
# {conversation_history}

# ## Student's Latest Message
# {latest_message_full}

# ## Your Task
# 1. **IDENTIFY INTENT** and provide tailored response
# 2. **Include "Your Next Steps"** - Bulleted list of 2-3 concrete actions
# 3. **Mention relevant UK resources**
# 4. **End with PROACTIVE SUGGESTIONS** - Based on their profile, suggest 2-3 related topics they might want to explore next. Format as:

# **You might also want to explore:**
# - [Topic 1 based on their major/interest]
# - [Topic 2 based on their year]
# - [Topic 3 based on their situation]

# This encourages continued engagement without explicitly asking "do you have more questions?"

# Generate your career advice response now:
# """

#         # ... [rest of your code] ...


# # ======================== Another suggestion ========================
# '''
# Improvement 8: Emotional Intelligence and Empathy

# Problem: Career anxiety is real. The bot should recognize and respond to emotional cues.

# Solution: Add empathy detection to your prompt.
# '''
# user_prompt = f"""
# ...

# ## Emotional Context Detection
# Analyze the student's message for emotional cues:
# - Anxiety/stress: "worried", "stressed", "nervous", "scared"
# - Confusion: "don't know", "confused", "lost", "unsure"
# - Excitement: "excited", "can't wait", "looking forward"
# - Frustration: "frustrated", "stuck", "difficult"

# If emotional cues detected, acknowledge them empathetically before providing advice.

# Examples:
# - Anxiety: "I can understand feeling worried about job prospects - it's completely normal. Let's break this down..."
# - Confusion: "Career planning can feel overwhelming when you're unsure where to start. Let's clarify..."
# - Excitement: "Love your enthusiasm! Let's channel that energy into a solid plan..."

# ## Student's Latest Message
# {latest_message_full}
# """



# # ======================== Another suggestion ========================
# '''
# Improvement 9: Multi-turn Clarification

# Problem: Sometimes the bot needs more information but asking feels abrupt.

# Solution: Add clarification collection within the action itself.
# '''
# """
# slots:
#   needs_clarification:
#     type: bool
#     mappings:
#       - type: from_llm
  
#   clarification_question:
#     type: text
#     mappings:
#       - type: controlled
# """
# # === DONE!

# class ActionGiveCareerAdvice(Action):
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
#         # Check if we need clarification
#         career_interest = tracker.get_slot("career_interest")
        
#         if not career_interest or career_interest == "not specified":
#             # Ask for clarification naturally
#             dispatcher.utter_message(
#                 text="I'd love to help! Could you tell me a bit more about what career area interests you? (e.g., tech, healthcare, finance, creative industries)"
#             )
#             return [SlotSet("needs_clarification", True)]
        
#         # ... proceed with advice generation ...


# # ======================== Another suggestion ========================
# # Dynamic response length based on user preference        
# """
# Problem: Some users want detailed explanations, others want quick answers.

# Solution: Detect user preference and adjust response length.

# Add a slot:
# slots:
#   response_preference:
#     type: categorical
#     values:
#       - brief
#       - detailed
#       - default
#     mappings:
#       - type: from_llm
#     """

# # Update system instructions 
# SYSTEM_INSTRUCTIONS = """
# ...

# ## Response Length Adaptation
# - If user says "keep it brief", "quick answer", "short version": Provide concise 100-150 word responses
# - If user says "tell me more", "detailed", "explain thoroughly": Provide comprehensive 250-350 word responses
# - Default: 150-250 words

# Detect user preference from their language and adjust accordingly.
# """