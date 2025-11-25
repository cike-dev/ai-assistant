# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.events import SlotSet

# # class ActionGetUserQuery(Action):
# #     def name(self):
# #         return "action_get_user_query"
    
# #     def run(self, 
# #             dispatcher: CollectingDispatcher,
# #             tracker: Tracker,
# #             domain: dict):
        
# #         # Get the user's message
# #         user_message = tracker.latest_message.get('text')
        
# #         # Save it to a slot
# #         return [SlotSet("user_query", user_message)]
    

# class ActionGiveCareerAdvice(Action):
#     def name(self):
#         return "action_give_career_advice"
    
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: dict):
        
#         # Get all user messages from the conversation
#         user_messages = [
#             event.get('text') 
#             for event in tracker.events 
#             if event.get('event') == 'user'
#         ]
        
#         # The LLM can extract the key query from all messages
#         conversation_context = " | ".join(user_messages[-5:])  # Last 5 messages

#         return [SlotSet("user_query", conversation_context)]
#         # This custom action will provide full context to the LLM for better advice
