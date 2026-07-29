import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

from chatbot_api.tools.cypher_tool import cypher_rag_tool, SCHEMA
from chatbot_api.tools.vector_tool import vector_rag_tool
from chatbot_api.tools.hybrid_tool import hybrid_rag_tool

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="openai/gpt-oss-20b:free",
    temperature=0,
    max_retries=3
)

system_message = f"""You are an intelligent recruiting assistant. You have access to three specific tools to answer questions. 
You MUST use EXACTLY ONE tool to answer the user's question. Read the tool descriptions carefully to decide which one to use. 

IMPORTANT NEO4J SCHEMA FOR CYPHER TOOLS:
{SCHEMA}

TOOL USAGE RULES:
1. `cypher_rag_tool`: Use for structured data aggregation (e.g., counting, averages, filtering by properties). YOU MUST write the Cypher query yourself based on the schema and pass it to this tool.
2. `hybrid_rag_tool`: Use when the query needs BOTH structured filtering AND unstructured text search (e.g., "Find candidates who left early AND look at their negative interview reviews"). YOU MUST write the Cypher query to extract the `id` of the entities, AND provide the semantic text search query.
3. `vector_rag_tool`: Use for general unstructured feedback across the entire database without specific graph entity filtering.

When writing Cypher queries for the tools, use standard Neo4j syntax. For date math, use `duration.inDays(date1, date2).days`.
DO NOT filter by sentiment, rating, or text in Cypher for the `hybrid_rag_tool` - let the Cypher just extract the structural entities (e.g. tenure < 12), and pass the sentiment requirement to the tool's semantic_search_query argument.
"""

tools = [cypher_rag_tool, vector_rag_tool, hybrid_rag_tool]

agent_executor = create_react_agent(llm, tools, prompt=system_message)

def invoke_agent(question: str) -> dict:
    result = agent_executor.invoke({"messages": [("user", question)]})
    return result
