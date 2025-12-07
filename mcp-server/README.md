# AI Assistant MCP Server

This is an MCP (Model Context Protocol) server that provides internet search capabilities using Tavily for a career counselling chatbot.

## Features

The server provides four main search tools:
- `search_job_market_trends`: Searches for job market trends in specific industries
- `find_salary_data`: Finds salary information for roles and job titles
- `get_industry_insights`: Provides insights about industries and sectors
- `search_career_paths`: Explores career advancement and path options

## Installation

1. Ensure Python 3.12+ is installed
2. Install dependencies:
   ```bash
   pip install -e .
   ```
   or if using uv:
   ```bash
   uv sync
   ```

## Environment Variables

Set the following environment variables:
- `TAVILY_API_KEY`: Your Tavily API key (required)

## Usage

### Running as MCP Server
```bash
python main.py
```

### Running as HTTP API Server
```bash
python api.py
# or
uvicorn api:app --reload
```

The HTTP API will be available at `http://localhost:8000` with endpoints:
- `GET /`: API information
- `POST /search/job_market_trends`
- `POST /search/salary_data`
- `POST /search/industry_insights`
- `POST /search/career_paths`

## Integration with Rasa

This server can be integrated with Rasa through:
1. MCP sub-agents (using stdio communication)
2. HTTP API calls from custom actions

## Dependencies

- mcp>=1.23.1: For MCP protocol support
- tavily-python: For internet search
- python-dotenv: For environment variable loading
- fastapi: For HTTP API (optional)
- uvicorn: For HTTP server (optional)
