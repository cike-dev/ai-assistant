# Student Support AI-Assistant

A lightweight AI assistant template designed to handle career guidance, general support, and school-related assistance.

---

## 🚀 What's Included

This project provides a versatile assistant with:
- **Career Support**: Advice, job search tips, and internship guidance
- **General Conversations**: Greetings, feedback collection, human handoff, and fallback handling
- **School Support**: Assistance related to academic and IT support topics
- **Knowledge Base**: FAQs, policies, and guides to help users with common questions
- **Custom Actions**: Extendable Python logic to handle complex tasks

---

## 📁 Directory Structure

├── actions/      # Custom Python logic for assistant operations
├── data/         # Conversation flows and training data
├── domain/       # Agent configuration (slots, responses, actions)
├── docs/         # Knowledge base documents and FAQs
├── models/       # Trained models for the assistant
├── prompts/      # LLM prompts for enhanced, contextual responses
├── tests/        # Automated tests and validation scenarios
├── za others/    # Notebooks for testing
├── config.yml    # Training pipeline and project configuration
├── credentials.yml     # Credentials for APIs and external services
├── endpoints.yml       # Endpoint definitions for custom actions and services
├── requirements.txt    # Python dependencies list

---
 
## Requirements:
- python 3.11
- IDE (VS Code, Pycharm, etc)
- uv package installer
- Mistralai API key
- Gemini API keys

---

## Setup Environment

#### 1. Install uv package installer
- **Windows:** 
```pwershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
- **Linux or MacOS:** 
```bash 
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. Create and activate virtual env
```bash
  mkdir my-rasa-assistant  
  cd my-rasa-assistant  
  uv venv --python 3.11 .rasa-env
``` 

**Activate:**  
- Windows: `.\.rasa-env\Scripts\activate`
- Linux or Mac: `source .rasa-env/bin/activate`

#### 3. Clone this repo
`git clone https://github.com/cike-dev/ai-assistant.git`  
`cd ai-assistant`

#### 4. Install requirements
`uv pip install -r requirements.txt`

**Set RASA_LICENSE Key**  
obtain license key: https://rasa.com/rasa-pro-developer-edition-license-key-request/   
For access to Rasa-pro developers edition

Method 1:  
- Create a .env file
- Edit the file and save your rasa license key like this:  
    `RASA_LICENSE="YOUR_LICENSE_KEY"`  

**Method 2:**  
Run this command:  
- Windows (powershell):  
      `[Environment]::SetEnvironmentVariable("RASA_LICENSE", "YOUR_LICENSE_KEY", "User")`  

- Linux or macOS:  
      `export RASA_LICENSE="YOUR_LICENSE_KEY"`  

**Confirm:**  
`rasa --version`  

#### 5. More configs for .env file
set llm health check:  
`LLM_API_HEALTH_CHECK="True"`  

save your api keys like this:  
`MISTRAL_API_KEY="YOUR OPENAI API KEY"`  
`GEMINI_API_KEY="YOUR GEMINI API KEY"`  

---

## Usage 
#### 1. Train a Model:
```sh 
 rasa train --domain domain
```

#### 2. Inspect: 
```sh
 rasa inspect
```