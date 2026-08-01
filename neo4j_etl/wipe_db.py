import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def wipe_db(driver):
    print("Starting batched DB wipe...")
    with driver.session() as session:
        while True:
            # Delete nodes in batches of 5000 to prevent OOM / timeouts
            result = session.run("""
                MATCH (n)
                WITH n LIMIT 5000
                DETACH DELETE n
                RETURN count(n) AS deleted_count
            """)
            deleted_count = result.single()["deleted_count"]
            print(f"Deleted {deleted_count} nodes...")
            if deleted_count == 0:
                break
    print("DB completely wiped.")


if __name__ == "__main__":
    try:
        wipe_db(driver)
    finally:
        driver.close()
