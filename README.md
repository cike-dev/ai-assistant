## Student Support AI-Assistant

### Requirements:
- python 3.12
- IDE (VS Code, Pycharm, etc)
- uv package installer
- OpenAI API key
- Gemini API key

### Setup Environment

#### 1. Install uv package installer
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Linux or MacOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`

#### 2. Create and activate virtual env
`mkdir my-rasa-assistant`  
`cd my-rasa-assistant`  
`uv venv --python 3.12 .rasa-env`  

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
- Create a new file, name it .env
- Edit the .env file and save your license key like this: `RASA_LICENSE="YOUR_LICENSE_KEY"`  

Method 2:  
on windows (pwsh): `[Environment]::SetEnvironmentVariable("RASA_LICENSE", "YOUR_LICENSE_KEY", "User")`  
Linux or macOS: `export RASA_LICENSE="YOUR_LICENSE_KEY"`  

**Confirm:**  
`rasa --version`  

#### 5. More configs for .env file
set llm health check:  
`LLM_API_HEALTH_CHECK="True"`  

save your api keys like this:  
`OPENAI_API_KEY="YOUR OPENAI API KEY"`  
`GEMINI_API_KEY="YOUR GEMINI API KEY"`  
