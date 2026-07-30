import os
from neo4j import GraphDatabase
from chatbot_api.tools.vector_tool import HFInferenceEmbeddings
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# We keep this just for reference, but the real data is in Neo4j now.
examples = []

def get_few_shot_prompt(question: str) -> str:
    """
    Retrieves semantically similar Cypher examples based on the question directly from Neo4j.
    """
    embeddings = HFInferenceEmbeddings()
    try:
        vector = embeddings.embed_query(question)
    except Exception as e:
        print(f"Error generating embedding for few-shot: {e}")
        return ""
        
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    query = """
    CALL db.index.vector.queryNodes('cypher_example_embeddings', 2, $query_vector)
    YIELD node AS example, score
    RETURN example.question AS question, example.cypherQuery AS query, score
    """
    
    try:
        with driver.session() as session:
            result = session.run(query, query_vector=vector)
            similar_examples = [record.data() for record in result]
    except Exception as e:
        print(f"Error querying Neo4j for few-shot examples: {e}")
        similar_examples = []
    finally:
        driver.close()
        
    if not similar_examples:
        return ""
        
    prompt_addition = "\n\nHere are some examples of correctly formatted Cypher queries for similar past questions:\n"
    for ex in similar_examples:
        prompt_addition += f"- User Question: {ex['question']}\n  Cypher Query: `{ex['query']}`\n"
        
    return prompt_addition
