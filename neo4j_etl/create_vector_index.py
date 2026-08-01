import os
import sys

# Ensure chatbot_api is in path so we can import the embeddings class
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from neo4j import GraphDatabase

from chatbot_api.tools.vector_tool import HFInferenceEmbeddings

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def ensure_vector_index(driver):
    print("Creating vector index if it doesn't exist...")
    with driver.session() as session:
        # Create vector index
        # 384 dimensions for sentence-transformers/all-MiniLM-L6-v2
        session.run("""
            CREATE VECTOR INDEX review_embeddings IF NOT EXISTS
            FOR (r:Review) ON (r.embedding)
            OPTIONS {indexConfig: {
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
            }}
        """)
    print("Vector index ensured.")


def backfill_embeddings(driver):
    embeddings_model = HFInferenceEmbeddings()
    batch_size = 100

    with driver.session() as session:
        print("Fetching reviews without embeddings...")
        result = session.run(
            "MATCH (r:Review) WHERE r.embedding IS NULL RETURN r.id AS id, r.text AS text"
        )
        reviews = [record.data() for record in result]
        total = len(reviews)
        print(f"Found {total} reviews to embed.")

        if total == 0:
            return

        processed = 0
        for i in range(0, total, batch_size):
            batch = reviews[i : i + batch_size]
            texts = [r["text"] for r in batch]
            ids = [r["id"] for r in batch]

            print(f"Embedding batch {i} to {i+len(batch)} of {total}...")
            # This handles retries and backoff automatically
            vectors = embeddings_model.embed_documents(texts)

            # Prepare parameters for Cypher UNWIND
            updates = [
                {"id": ids[j], "embedding": vectors[j]} for j in range(len(batch))
            ]

            # Write back to Neo4j
            session.execute_write(
                lambda tx: tx.run(
                    """
                    UNWIND $updates AS update
                    MATCH (r:Review {id: update.id})
                    SET r.embedding = update.embedding
                """,
                    updates=updates,
                )
            )
            processed += len(batch)
            print(f"  Successfully saved {processed}/{total} embeddings.")


if __name__ == "__main__":
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        ensure_vector_index(driver)
        backfill_embeddings(driver)
        print("Done!")
    finally:
        driver.close()
