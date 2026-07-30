import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from chatbot_api.tools.vector_tool import HFInferenceEmbeddings
from chatbot_api.few_shot import examples

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def seed_examples():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    embeddings = HFInferenceEmbeddings()

    # Create vector index
    index_query = """
    CREATE VECTOR INDEX cypher_example_embeddings IF NOT EXISTS
    FOR (e:CypherExample)
    ON (e.embedding)
    OPTIONS {indexConfig: {
     `vector.dimensions`: 384,
     `vector.similarity_function`: 'cosine'
    }}
    """
    
    with driver.session() as session:
        print("Creating vector index...")
        session.run(index_query)
        
        # Check if already seeded
        count = session.run("MATCH (e:CypherExample) RETURN count(e) as c").single()["c"]
        if count > 0:
            print(f"Already found {count} CypherExamples. Clearing them to re-seed...")
            session.run("MATCH (e:CypherExample) DETACH DELETE e")
        
        print("Embedding and storing examples...")
        for i, ex in enumerate(examples):
            question = ex["question"]
            query = ex["query"]
            print(f"Embedding [{i+1}/{len(examples)}]: {question}")
            
            vector = embeddings.embed_query(question)
            
            session.run("""
            CREATE (e:CypherExample {
                id: randomUUID(),
                question: $question,
                cypherQuery: $cypherQuery,
                embedding: $embedding
            })
            """, question=question, cypherQuery=query, embedding=vector)
            
    driver.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_examples()
