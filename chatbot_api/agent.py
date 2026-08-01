import os

from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI

# pyrefly: ignore [missing-import]
from langgraph.prebuilt import create_react_agent

from chatbot_api.tools.cypher_tool import SCHEMA, cypher_rag_tool
from chatbot_api.tools.hybrid_tool import hybrid_rag_tool
from chatbot_api.tools.vector_tool import vector_rag_tool

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if os.getenv("USE_HF_MOCK") == "1":
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

    hf = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.3", max_new_tokens=512
    )
    llm = ChatHuggingFace(llm=hf)
else:
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        model="openai/gpt-oss-20b:free",
        temperature=0,
        max_retries=3,
    )

from langgraph.checkpoint.memory import MemorySaver

from chatbot_api.few_shot import get_few_shot_prompt

system_message_base = f"""You are an intelligent recruiting assistant. You have access to three specific tools to answer questions. 
You MUST use EXACTLY ONE tool to answer the user's question. Read the tool descriptions carefully to decide which one to use. 

IMPORTANT NEO4J SCHEMA FOR CYPHER TOOLS:
{SCHEMA}

TOOL USAGE RULES:
1. `cypher_rag_tool`: Use for structured data aggregation (e.g., counting, averages, filtering by properties). YOU MUST write the Cypher query yourself based on the schema and pass it to this tool. **CRITICAL for "Attrition Insights":** When asked about the correlation between interview experience/sentiment and employee tenure (e.g. "What is the general interview sentiment of candidates who were hired but left within 6 months?"), DO NOT use text sentiment. Instead, use Cypher to prove the structural correlation.
   **Avoid Circular Evidence:** Do NOT filter for "left within 6 months" and then report that their average tenure is ~3 months. That is circular.
   Instead, your synthesis MUST lead with these two pieces of evidence:
   - The **full-population bucketed trend**: Compute average `tenure_months` for ALL employees bucketed by interview rating (1-2, 3, 4-5).
   - The **baseline-normalized proportion**: Compare the percentage of ALL employees who gave a 1-2 rating versus the percentage of the early-leaver cohort (left within 6 months) who gave a 1-2 rating.
   You may need to run more than one Cypher query to get both the full population trend and the specific cohort counts.
   **IMPORTANT:** After gathering the structural facts, you MUST use the `vector_rag_tool` to fetch a few illustrative text examples of negative interview experiences to add color to your final answer.
2. `hybrid_rag_tool`: Use when the query needs BOTH structured filtering AND unstructured text search strictly scoped to those entities. (Note: For Attrition Insights rating vs tenure, prefer pure Cypher for the proof, and use Vector separately for color).
3. `vector_rag_tool`: Use for general unstructured feedback across the entire database without specific graph entity filtering. Or use it to fetch a few illustrative text examples (e.g., "negative interview experience") AFTER you have established the structural facts.

When writing Cypher queries for the tools, use standard Neo4j syntax. For date math, use `duration.inDays(date1, date2).days`.
"""


def dynamic_prompt(state):
    # Extract latest user message
    messages = state.get("messages", [])
    user_msg = ""
    for msg in reversed(messages):
        if msg.type == "user":
            user_msg = msg.content
            break

    few_shot = get_few_shot_prompt(user_msg) if user_msg else ""

    return [("system", system_message_base + few_shot)] + messages


tools = [cypher_rag_tool, vector_rag_tool, hybrid_rag_tool]
memory = MemorySaver()

agent_executor = create_react_agent(
    llm, tools, prompt=dynamic_prompt, checkpointer=memory
)


async def invoke_agent(
    question: str, thread_id: str = "default_session", callbacks=None
) -> dict:
    config = {"configurable": {"thread_id": thread_id}}
    if callbacks:
        config["callbacks"] = callbacks

    result = await agent_executor.ainvoke(
        {"messages": [("user", question)]}, config=config
    )
    return result
