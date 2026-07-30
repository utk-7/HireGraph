from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()
driver = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')))
with driver.session() as session:
    res = session.run('MATCH (e:CypherExample) RETURN e.question AS question, e.cypherQuery AS query')
    records = [r.data() for r in res]
    for i, r in enumerate(records):
        print(f'{i+1}. {r["question"]}')
