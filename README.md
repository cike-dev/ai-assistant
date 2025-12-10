# Student Support AI-Assistant

A modern, lightweight AI assistant designed to provide career guidance, general support, and school-related assistance. This project leverages **Rasa Pro** with CALM (Conversational ALM), an **MCP (Model Context Protocol)** server for real-time web search, and a **Streamlit** user interface.

---

## 🚀 Features

-   **Career Support**: Real-time job market trends, salary data, and career path advice using Tavily search.
-   **Campus Support**: RAG-based answers for university-specific queries (e.g., University of Wolverhampton).
-   **General Conversations**: Handle greetings, chit-chat, and fallback scenarios gracefully.
-   **Modern Stack**: Built with Rasa Pro 3.14+, Gemini/Mistral LLMs, and Model Context Protocol (MCP).

---

## 📁 Directory Structure

```text
├── actions/            # Custom Python actions for Rasa
├── chat_ui/            # Streamlit-based chat interface
│   └── my_app_2.py     # Main UI application
├── data/               # Rasa training data (flows, NLU, rules)
├── docs/               # RAG knowledge base documents
├── domain/             # Rasa domain configuration
├── mcp-server/         # MCP Server for external tools (Search, etc.)
│   ├── main_1.py       # Main entry point for MCP server
│   └── pyproject.toml  # MCP server dependencies
├── tests/              # End-to-end tests
├── config.yml          # Rasa pipeline & policy config
├── endpoints.yml       # Endpoint definitions (MCP, Action Server, LLMs)
└── requirements.txt    # Project Desktop/client dependencies
```

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following:

-   **Python 3.12** (Required for Rasa Pro compatibility)
-   **uv** (Recommended package manager)
-   **Rasa Pro License** (Required for using Rasa Pro features)
-   **API Keys**:
    -   Mistral AI (for RAG/Embeddings)
    -   Gemini (for Command Generation/LLM)
    -   Tavily (for Search Tools)

---

## 📦 Installation

### 1. Install `uv`
**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Set up the Main Environment
1.  Clone this repository:
    ```bash
    git clone https://github.com/cike-dev/ai-assistant.git
    cd ai-assistant
    ```
2.  Create and activate a virtual environment:
    ```bash
    uv venv --python 3.12 .rasa-env
    # Windows
    .\.rasa-env\Scripts\activate
    # Linux/macOS
    source .rasa-env/bin/activate
    ```
3.  Install dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```

### 3. Set up the MCP Server Environment
The MCP server runs in its own environment to avoid conflict:
```bash
cd mcp-server
uv sync
# This reads pyproject.toml and installs dependencies like mcp, tavily-python, fastmcp
cd ..
```

---

## 🔑 Configuration

### 1. Environment Variables (`.env`)
Create a `.env` file in the root directory and add your keys:

```ini
# Rasa License (Required)
RASA_LICENSE="Your_Rasa_Pro_License_Key"

# LLM Providers
MISTRAL_API_KEY="Your_Mistral_Key"
GEMINI_API_KEY="Your_Gemini_Key"
# If using different keys for specific components as per config.yml:
GEMINI_PIPELINE="Your_Gemini_Key"
GEMINI_POLICY="Your_Gemini_Key"
GEMINI_REPHRASER="Your_Gemini_Key"

# Search Tools
TAVILY_API_KEY="Your_Tavily_Key"

# Configuration
LLM_API_HEALTH_CHECK="True"
```

Also, ensure your `mcp-server/.env` exists if it requires separate loading, though usually, the root `.env` is sufficient if loaded correctly. *Note: The MCP server script `main_1.py` loads `.env` explicitly.*

---

## ▶️ Running the Application

You will need to run **four** separate terminal processes.

### Terminal 1: MCP Server
This provides the search tools to Rasa.
```bash
# Navigate to mcp-server folder
cd mcp-server

# Run the server (defaults to port 8080)
python main_1.py
```

### Terminal 2: Rasa Action Server
Runs custom actions defined in the `actions/` directory.
```bash
# From root directory, with .rasa-env activated
rasa run actions
```

### Terminal 3: Rasa Core (Agent)
Runs the main Rasa server with API enabled.
```bash
# From root directory, with .rasa-env activated
rasa run --enable-api --cors "*" --debug
```

### Terminal 4: Streamlit UI
Launches the chat interface.
```bash
# From root directory, with .rasa-env activated
streamlit run chat_ui/my_app_2.py
```

---

## 🧪 Development & Testing

### Train the Model
```bash
rasa train
```

### Inspector (Debug Mode)
To inspect the conversation flow and CALM reasoning:
```bash
rasa inspect
```

### End-to-End Testing
To run the end-to-end tests and generate a coverage report:
```bash
rasa test e2e tests --coverage-report --coverage-output-path coverage_reports
```
