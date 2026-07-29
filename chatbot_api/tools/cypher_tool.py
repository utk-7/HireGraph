import os
from typing import Dict, Any
from neo4j import GraphDatabase
from langchain_core.tools import tool
from dotenv import load_dotenv

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
- Offer: id, offer_date, decision_date, status, base_salary, equity, sign_on_bonus
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
    try:
        with driver.session() as session:
            result = session.run(cypher_query)
            records = [record.data() for record in result]
            if not records:
                return f"Cypher Query executed:\n{cypher_query}\n\nResult: No matching records found."
            return f"Cypher Query executed:\n{cypher_query}\n\nResult:\n{records}"
    except Exception as e:
        return f"Database Error executing Cypher: {e}\nQuery attempted:\n{cypher_query}"
    finally:
        driver.close()
