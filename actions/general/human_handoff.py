from typing import Any, Dict, List, Text

import os
import google.genai as genai
from google.genai import types

from rasa_sdk import Action, Tracker
from rasa_sdk.events import BotUttered
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ActionHumanHandoff(Action):
    def __init__(self) -> None:
        super().__init__()
        # self.client = AsyncOpenAI()

        self.client = genai.Client(
            # api_key="AIzaSyDcpzEpbH-1cfm789VpkEsgnphd7rnjDzs"
            api_key=os.getenv("GEMINI_SEARCH_GROUNDING")
        )

    def name(self) -> Text:
        return "action_human_handoff"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        # Collect conversation
        convo = []
        for event in tracker.events:
            # user messages
            if event.get("event") == "user":
                user_text = "{}".format(event.get("text"))
                user_text2 = "user - " + user_text
                convo.append(user_text2)
            
            # bot responses
            if event.get("event") == "bot":
                bot_text = "{}".format(event.get("text"))
                bot_text2 = "bot - " + bot_text
                # print(bot_text)
                convo.append(bot_text2)
        
        prompt = (
            f"The following is a conversation between a bot and a human user, "
            f"please summarise the conversation, clearly highlighting the student's main questions or issues,"
            f"relevant background (such as major, year, or context), and indicate which service area is most relevant for human follow-up. "
            f"Make the summary concise and actionable so a human agent or school contact can quickly understand and assist the student appropriately. "
            f"Conversation: {convo}"
        )
        
        config = types.GenerateContentConfig(
            response_modalities=["TEXT"],
            # system_instruction=
            # [
            #   'You are a helpful language translator.',
            #   'Your mission is to translate text in English to French.'
            # ]
        )
     
        response = await self.client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config,
        )
        summarised_conversation = response.text.strip() or ""
        
        return [
            BotUttered(
                f"This is a summary of our conversation"
                f"Notify them with this info:\n"
                f"{summarised_conversation}"
            )
        ]
