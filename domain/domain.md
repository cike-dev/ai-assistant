## 📂 `domain/` – The Agent's Brain

This folder contains YAML files that define the AI assistant’s core components:
- **Slots**: The agent's memory for storing information during conversations (e.g., user preferences, context, intents).
- **Responses**: The messages your agent can say to users (e.g., greetings, confirmations, advice).
- **Actions**: Custom logic the agent can execute to handle tasks or fetch data.

**What you'll find:**
- **career/**: Domain configurations related to career advice and guidance
- **general/**: General domain elements including greetings, feedback, human handoff, and conversation patterns
- **other/**: Shared resources and fallback mechanisms for unrecognized input
- **school/**: Domain files focused on school support and related assistance

You can organize the domain as one big file or many smaller ones. Rasa will automatically merge all domain files during training.
