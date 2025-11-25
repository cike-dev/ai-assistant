# actions/__init__.py

# from actions.career.career_advice import ActionGiveCareerAdvice
# from actions.career.career_advice import ActionFollowupCareerAdvice

# from actions.career.gemini_advice import (
#     ActionGiveCareerAdvice,
#     ActionFollowupCareerAdvice
# )

# from actions.career.get_user_query import ActionGetUserQuery

from actions.career.ai_adviser import ActionGiveCareerAdvice

from actions.school_support.sch_check_rag_success import ActionCheckRagResult

from actions.general.slots_validation import ValidateCareerAdviceForm

# # Suppress Pydantic UserWarnings
import warnings
# Suppress all UserWarnings related to Pydantic serialization
warnings.filterwarnings(
    "ignore", 
    message="Pydantic serializer warnings:.*", 
    category=UserWarning, 
    module='pydantic'
)

# from actions.general.human_handoff import ActionHumanHandoff

# logger setup
from actions.general.logger_utils import get_logger

# load environment variables
from dotenv import load_dotenv
load_dotenv()
