from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tavily import TavilyClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY environment variable must be set")

tavily_client = TavilyClient(api_key=tavily_api_key)

app = FastAPI(title="AI Assistant Search API", description="API for career counselling search tools using Tavily")

class SearchRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "AI Assistant Search API", "tools": ["job_market_trends", "salary_data", "industry_insights", "career_paths"]}

@app.post("/search/job_market_trends")
async def search_job_market_trends(request: SearchRequest):
    try:
        response = tavily_client.search(
            query=f"job market trends {request.query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = [f"- {result['title']}: {result['url']}" for result in response.get("results", [])]
        return {
            "answer": answer,
            "sources": results,
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching job market trends: {str(e)}")

@app.post("/search/salary_data")
async def find_salary_data(request: SearchRequest):
    try:
        response = tavily_client.search(
            query=f"salary data {request.query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = [f"- {result['title']}: {result['url']}" for result in response.get("results", [])]
        return {
            "answer": answer,
            "sources": results,
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding salary data: {str(e)}")

@app.post("/search/industry_insights")
async def get_industry_insights(request: SearchRequest):
    try:
        response = tavily_client.search(
            query=f"industry insights {request.query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = [f"- {result['title']}: {result['url']}" for result in response.get("results", [])]
        return {
            "answer": answer,
            "sources": results,
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting industry insights: {str(e)}")

@app.post("/search/career_paths")
async def search_career_paths(request: SearchRequest):
    try:
        response = tavily_client.search(
            query=f"career paths {request.query}",
            include_answer=True,
            search_depth="advanced"
        )
        answer = response.get("answer", "")
        results = [f"- {result['title']}: {result['url']}" for result in response.get("results", [])]
        return {
            "answer": answer,
            "sources": results,
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching career paths: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
