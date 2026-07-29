import json
from neo4j import GraphDatabase
import os

from dotenv import load_dotenv
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

with open("data/generated/pattern_targets.json", "r") as f:
    targets = json.load(f)

attrition_ids = [t["cand_id"] for t in targets["attrition"]]
control_ids = [t["cand_id"] for t in targets["control"]]
all_ids = attrition_ids + control_ids

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_data():
    with driver.session() as session:
        # Get Candidate -> Employee tenure
        cypher = """
        MATCH (c:Candidate)-[:HIRED_AS]->(e:Employee)
        WHERE c.id IN $ids
        RETURN c.id AS id, e.tenure_months AS tenure, e.still_employed AS still_employed
        """
        result = session.run(cypher, ids=all_ids)
        for record in result:
            print(f"Candidate: {record['id']}, Tenure: {record['tenure']}, Still Employed: {record['still_employed']}")
            
        # Get Reviews
        print("\nREVIEWS:")
        cypher_reviews = """
        MATCH (c:Candidate)
        WHERE c.id IN $ids
        MATCH (c)-[:WROTE]->(r:Review)
        RETURN c.id AS id, r.review_type AS type, r.text AS text
        """
        rev_result = session.run(cypher_reviews, ids=all_ids)
        for r in rev_result:
            print(f"[{r['id']}] {r['type']}: {r['text'][:100]}...")

get_data()
driver.close()
