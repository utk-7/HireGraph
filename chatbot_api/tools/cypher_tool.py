import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.tools import tool
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

SCHEMA = """
Nodes:
- Company: id, name, industry, size, headquarters, founded_year, rating
- Department: id, name
- JobPosting: id, title, level, salary_min, salary_max, status, posted_date, remote_type
- Candidate: id, name, years_experience, location, source
- Application: id, applied_date, current_stage, status
- Interview: id, round_number, interview_type, interview_date, status, feedback_score
- Recruiter: id, name, seniority
- Interviewer: id, name, role
- Offer: id, extended_date, decision_date, decision, base_salary, equity, bonus
- Employee: id, name, hire_date, still_employed, tenure_months, role
- Review: id, review_type (interview_experience|employee_experience), text, review_date, embedding

Relationships:
- (Company)-[:HAS_DEPARTMENT]->(Department)
- (Department)-[:POSTED]->(JobPosting)
- (Candidate)-[:SUBMITTED]->(Application)
- (Application)-[:FOR_POSTING]->(JobPosting)
- (Application)-[:MANAGED_BY]->(Recruiter)
- (Application)-[:HAS_INTERVIEW]->(Interview)
- (Interview)-[:CONDUCTED_BY]->(Interviewer)
- (Application)-[:RESULTED_IN]->(Offer)
- (Candidate)-[:HIRED_AS]->(Employee)
- (Employee)-[:WORKS_IN]->(Department)
- (Candidate)-[:WROTE]->(Review)
- (Review)-[:ABOUT]->(JobPosting)
"""


@tool
def cypher_rag_tool(cypher_query: str) -> str:
    """
    Executes a Cypher query against the Neo4j database to retrieve structured graph data.
    The query must be a valid Neo4j Cypher query based on the provided schema.
    Returns the stringified JSON records found.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def run_query(query: str):
        with driver.session() as session:
            result = session.run(query)
            records = [record.data() for record in result]
            summary = result.consume()

            # Neo4j doesn't throw exceptions for missing properties, it just emits warnings and returns null/empty.
            # We must catch these warnings and throw an exception to trigger the repair loop!
            if summary.notifications:
                warnings = []
                for n in summary.notifications:
                    if hasattr(n, "description"):
                        warnings.append(n.description)
                    elif isinstance(n, dict) and "description" in n:
                        warnings.append(n["description"])
                    else:
                        warnings.append(str(n))
                raise Exception(
                    "Database Warnings (treat as error to repair): "
                    + "; ".join(warnings)
                )

            if not records:
                return (
                    f"Cypher Query executed:\n{query}\n\nResult: No matching records found.",
                    True,
                )
            return f"Cypher Query executed:\n{query}\n\nResult:\n{records}", True

    try:
        try:
            msg, success = run_query(cypher_query)
            return msg
        except Exception as e:
            print(f"\n[Cypher Tool] Caught Error/Warning: {e}")
            print("[Cypher Tool] Initiating LLM Repair Loop...")
            # First attempt failed. Let's repair it exactly once.
            from langchain_openai import ChatOpenAI

            repair_prompt = f"""You are a Neo4j Cypher expert. The following Cypher query failed to execute due to a database error.
            
Query:
{cypher_query}

Error:
{e}

Schema:
{SCHEMA}

Please correct the Cypher query. Output ONLY the corrected Cypher query, nothing else. Do not use markdown blocks, just the query."""

            if os.getenv("USE_HF_MOCK") == "1":
                from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

                hf = HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.3", max_new_tokens=512
                )
                repair_llm = ChatHuggingFace(llm=hf)
            else:
                from langchain_openai import ChatOpenAI

                repair_llm = ChatOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    model="openai/gpt-oss-20b:free",
                    temperature=0,
                )

            repaired_query_response = repair_llm.invoke(repair_prompt).content.strip()
            # Clean up markdown if the LLM still used it
            if repaired_query_response.startswith("```cypher"):
                repaired_query_response = (
                    repaired_query_response.replace("```cypher", "")
                    .replace("```", "")
                    .strip()
                )
            elif repaired_query_response.startswith("```"):
                repaired_query_response = repaired_query_response.replace(
                    "```", ""
                ).strip()

            print(f"[Cypher Tool] Repaired Query:\n{repaired_query_response}")

            # Attempt to execute the repaired query
            try:
                msg, success = run_query(repaired_query_response)
                return msg
            except Exception as e2:
                # Retry also failed. Clean failure message.
                return "I'm sorry, I was unable to execute the database query due to a structural error that could not be repaired."
    finally:
        driver.close()
