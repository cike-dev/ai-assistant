from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
import logging

logger = logging.getLogger(__name__)

class ValidateCareerAdviceForm(ValidationAction):
    def name(self) -> Text:
        return "validate_career_advice"
    
    def validate_student_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Allow skipping name"""
        
        if slot_value:
            # Check if user wants to skip
            skip_phrases = ["skip", "prefer not", "don't want", "no thanks", "pass"]
            if any(phrase in slot_value.lower() for phrase in skip_phrases):
                return {"student_name": "Student"}
        
        return {"student_name": slot_value}
    
    def validate_year_of_study(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Allow skipping year"""
        
        if slot_value:
            skip_phrases = ["skip", "prefer not", "don't know", "not sure"]
            if any(phrase in slot_value.lower() for phrase in skip_phrases):
                return {"year_of_study": "not_specified"}
        
        return {"year_of_study": slot_value}
    
    def validate_gpa(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Allow skipping GPA"""
        
        if slot_value:
            skip_phrases = ["skip", "prefer not", "private", "don't want", "pass"]
            if any(phrase in slot_value.lower() for phrase in skip_phrases):
                return {"gpa": "not_provided"}
        
        return {"gpa": slot_value}
    
    def validate_has_internship(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Allow skipping internship question"""
        
        # If they explicitly skip, set to None
        if slot_value is None or (isinstance(slot_value, str) and 
                                   any(phrase in slot_value.lower() 
                                       for phrase in ["skip", "prefer not", "pass"])):
            return {"has_internship": None}
        
        return {"has_internship": slot_value}
    
    def validate_visa_status(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Allow skipping visa status"""
        
        if slot_value:
            skip_phrases = ["skip", "prefer not", "not relevant"]
            if any(phrase in slot_value.lower() for phrase in skip_phrases):
                return {"visa_status": "not_specified"}
        
        return {"visa_status": slot_value}