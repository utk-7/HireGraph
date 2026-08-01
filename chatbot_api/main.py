import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from neo4j import GraphDatabase
from pydantic import BaseModel

from chatbot_api.agent import invoke_agent

load_dotenv()

app = FastAPI(title="HireGraph API")


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    show_attrition_chart: bool


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = await invoke_agent(request.message, thread_id=request.session_id)
        response_text = result["messages"][-1].content

        # Simple heuristic to determine if the chart should be shown
        keywords = ["attrition", "left early", "6 months", "tenure", "rating"]
        msg_lower = request.message.lower()
        show_chart = any(k in msg_lower for k in keywords)

        return ChatResponse(response=response_text, show_attrition_chart=show_chart)
    except Exception as e:
        import traceback

        # Check if this is an openai RateLimitError (which openrouter uses)
        if e.__class__.__name__ == "RateLimitError" or "Rate limit" in str(e):
            # We don't need a loud traceback for a known rate limit exhaustion
            raise HTTPException(
                status_code=429, detail="OpenRouter rate limit exceeded."
            )

        # For genuinely unexpected errors, print the full traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/attrition_data")
async def get_attrition_data():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    query = """
    MATCH (c:Candidate)-[:WROTE]->(r:Review {review_type: 'interview_experience'}), (c)-[:HIRED_AS]->(e:Employee)
    WHERE r.rating IS NOT NULL AND e.tenure_months IS NOT NULL
    WITH e, 
      CASE 
        WHEN r.rating <= 2 THEN '1-2 (Negative)'
        WHEN r.rating = 3 THEN '3 (Neutral)'
        ELSE '4-5 (Positive)'
      END AS bucket,
      CASE WHEN e.tenure_months <= 6 THEN 1 ELSE 0 END AS is_early_leaver
    WITH bucket, count(*) as bucket_total, sum(is_early_leaver) as bucket_early_leavers, avg(e.tenure_months) as avg_tenure
    WITH collect({bucket: bucket, total: bucket_total, early_leavers: bucket_early_leavers, avg_tenure: avg_tenure}) as buckets
    UNWIND buckets as b
    WITH b, 
         reduce(s=0, x in buckets | s + x.total) as overall_total, 
         reduce(s=0, x in buckets | s + x.early_leavers) as overall_early_leavers
    RETURN 
      b.bucket as rating_bucket, 
      b.avg_tenure as avg_tenure_months,
      b.total as count,
      toFloat(b.total) / overall_total * 100 as baseline_pct,
      toFloat(b.early_leavers) / overall_early_leavers * 100 as early_leaver_pct
    ORDER BY rating_bucket
    """

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
        driver.close()
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
