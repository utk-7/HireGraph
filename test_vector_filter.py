from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv('.env')

driver = GraphDatabase.driver(
    os.getenv('NEO4J_URI'), 
    auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
)

with driver.session() as session:
    # Test if vector index accepts a WHERE clause or if we have to use the newer db.index.vector.queryNodes
    # Wait, in AuraDB, the typical way is to filter post-yield
    q = """
    CALL db.index.vector.queryNodes('review_embeddings', 10, $vec) YIELD node, score
    WHERE node.review_type = 'interview_experience'
    RETURN node.id, score LIMIT 1
    """
    res = session.run(q, vec=[0.1]*384)
    print("Post-filter:", [r.data() for r in res])

driver.close()
