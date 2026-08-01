import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

labels = [
    "Company",
    "Department",
    "JobPosting",
    "Candidate",
    "Application",
    "Interview",
    "Recruiter",
    "Interviewer",
    "Offer",
    "Employee",
    "Review",
]
rels = [
    "HAS_DEPARTMENT",
    "POSTED",
    "SUBMITTED",
    "FOR_POSTING",
    "MANAGED_BY",
    "HAS_INTERVIEW",
    "CONDUCTED_BY",
    "RESULTED_IN",
    "HIRED_AS",
    "WORKS_IN",
    "WROTE",
    "ABOUT",
]

with driver.session() as session:
    print("--- NODES ---")
    for label in labels:
        count = session.run(f"MATCH (n:{label}) RETURN count(n) AS c").single()["c"]
        print(f"{label}: {count}")

    print("\n--- REVIEWS BY TYPE ---")
    int_revs = session.run(
        "MATCH (r:Review {review_type: 'interview_experience'}) RETURN count(r) AS c"
    ).single()["c"]
    emp_revs = session.run(
        "MATCH (r:Review {review_type: 'employee_experience'}) RETURN count(r) AS c"
    ).single()["c"]
    print(f"Interview Experience: {int_revs}")
    print(f"Employee Experience: {emp_revs}")

    print("\n--- RELATIONSHIPS ---")
    for rel in rels:
        count = session.run(f"MATCH ()-[r:{rel}]->() RETURN count(r) AS c").single()[
            "c"
        ]
        print(f"{rel}: {count}")

driver.close()
