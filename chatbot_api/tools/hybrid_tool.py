import os

from langchain_core.tools import tool
from neo4j import GraphDatabase

from chatbot_api.tools.cypher_tool import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from chatbot_api.tools.vector_tool import HFInferenceEmbeddings


def scoped_vector_search(ids: list[str], question: str, top_k: int = 5) -> list[dict]:
    embeddings = HFInferenceEmbeddings()
    query_vector = embeddings.embed_query(question)

    cypher_query = """
    MATCH (entity) WHERE entity.id IN $id_list
    MATCH (entity)-[:WROTE|ABOUT|HAS_DEPARTMENT|POSTED|SUBMITTED|RESULTED_IN|HIRED_AS|WORKS_IN*1..4]-(r:Review)
    WHERE r.embedding IS NOT NULL
    WITH DISTINCT r
    RETURN r.text AS text, r.review_type AS type, vector.similarity.cosine(r.embedding, $query_vector) AS score
    ORDER BY score DESC LIMIT $top_k
    """

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session() as session:
            result = session.run(
                cypher_query, id_list=ids, query_vector=query_vector, top_k=top_k
            )
            return [record.data() for record in result]
    finally:
        driver.close()


@tool
def hybrid_rag_tool(cypher_query: str, semantic_search_query: str) -> str:
    """
    Executes a hybrid Graph+Vector search.
    - cypher_query: A Cypher query that MUST return a single column named `id`. It should filter the graph for the specific entities (e.g. Candidates) relevant to the user's question based strictly on structural properties (dates, tenure, status, relationships). DO NOT filter by sentiment in Cypher.
    - semantic_search_query: A natural language query describing what to search for in the unstructured text reviews connected to those filtered IDs (e.g., "negative interview feedback").

    Returns the unstructured review snippets specifically connected to the IDs found by the Cypher query.
    """
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        # Step 1: Execute Cypher to get IDs
        with driver.session() as session:
            result = session.run(cypher_query)
            entity_ids = []
            for record in result:
                val = record.get("id") if "id" in record else record.values()[0]
                if val:
                    entity_ids.append(val)

        if not entity_ids:
            return f"Cypher Query executed:\n{cypher_query}\n\nResult: No matching entities found for the Cypher filter."

        # Step 2: Scoped Vector Search
        reviews = scoped_vector_search(entity_ids, semantic_search_query)
        if not reviews:
            return f"Cypher Query executed:\n{cypher_query}\n\nResult: Found {len(entity_ids)} matching entities in the database, but none of them had relevant reviews for the semantic query '{semantic_search_query}'."

        # Format contexts for LLM
        filter_context = f"Found {len(entity_ids)} entities matching the criteria using Cypher query:\n{cypher_query}"
        reviews_context = "\n---\n".join(
            [
                f"Type: {r['type']}\nText: {r['text']}\n(Relevance Score: {r['score']:.2f})"
                for r in reviews
            ]
        )

        return f"{filter_context}\n\nRelevant Reviews Found (Scoped to those entities):\n{reviews_context}"
    except Exception as e:
        return f"Error executing Hybrid Tool: {e}\nCypher Attempted:\n{cypher_query}"
    finally:
        driver.close()
