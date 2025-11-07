from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from .logger_utils import get_logger

# Initialize a logger for this global setup block
logger = get_logger("sch_check_rag_success.py")

class ActionCheckRagResult(Action):
    def name(self) -> Text:
        return "action_check_rag_success"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Get the most recent bot event
        last_bot_event = None
        for event in reversed(tracker.events):
            if event.get("event") == "bot":
                last_bot_event = event
                logger.info("\n RAG_RESULT_CHECK: confirmed! last event was response by bot")
                break
        
        # Check for failure indicators in the bot's response
        failure_responses = [
            "utter_no_knowledge_base",
            "utter_no_relevant_answer_found"
        ]
        
        rag_succeeded = True  # Default to success
        
        if last_bot_event:
            # Check if it was a failure response
            response_name = last_bot_event.get("metadata", {}).get("utter_action")
            if response_name in failure_responses:
                rag_succeeded = False
                logger.info("RAG_RESULT_CHECK: RAG was unsuccessful! \n")
            else:
                logger.info("RAG_RESULT_CHECK: RAG was successful!\n")
        
        return [SlotSet("rag_result_found", rag_succeeded)]