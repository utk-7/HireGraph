import os
from dotenv import load_dotenv
from chatbot_api.tools.cypher_tool import cypher_rag_tool

load_dotenv()

def main():
    print("Testing malformed Cypher query that requires repair...")
    # This query uses an invalid property `fake_rating` which doesn't exist,
    # or an invalid relationship direction. Let's use a syntax error or non-existent property
    # Wait, neo4j allows non-existent properties (it just returns null).
    # To trigger a Neo4j driver error, we should use a syntax error or a non-existent relationship type that violates schema if type checking is on, OR a function that fails.
    # Actually, a syntax error is easiest:
    bad_query = "MATCH (c:Candidate)--[WROTE]->(r:Review) RETRN c.name" # RETRN instead of RETURN
    
    print(f"Calling tool with query: {bad_query}")
    result = cypher_rag_tool.invoke({"cypher_query": bad_query})
    
    print("\nResult from tool:")
    print(result)

if __name__ == "__main__":
    main()
