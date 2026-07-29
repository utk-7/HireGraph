import sys
import os
import json

# Ensure chatbot_api is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from chatbot_api.tools.cypher_tool import text_to_cypher_tool
from chatbot_api.tools.vector_tool import vector_rag_tool

def test_cypher():
    questions = [
        "Which department has the longest average time-to-offer?",
        "How many candidates applied to Miller, Brennan and Berry?",
        "What is the average base salary for offers at Finance?",
        "Which recruiter has managed the most applications?",
        "How many employees are still employed vs. no longer employed?"
    ]
    
    print("=======================================")
    print("      TEXT-TO-CYPHER (GRAPH) TOOL      ")
    print("=======================================")
    for idx, q in enumerate(questions):
        print(f"\nQ{idx+1}: {q}")
        res = text_to_cypher_tool(q)
        if "error" in res:
            print("ERROR:", res["error"])
        else:
            print("CYPHER:\n" + res["cypher"])
            print("RESULTS:\n" + json.dumps(res["results"], indent=2))

def test_vector():
    questions = [
        "What do candidates say about interviews for Lead Sales Manager?",
        "Find reviews mentioning round 3 being a disaster",
        "What negative feedback exists about the Finance department?",
        "Show me positive employee reviews about company culture",
        "What do employees who left the company say about their experience?"
    ]
    
    print("\n=======================================")
    print("            VECTOR RAG TOOL            ")
    print("=======================================")
    for idx, q in enumerate(questions):
        print(f"\nQ{idx+1}: {q}")
        res = vector_rag_tool(q, top_k=3)
        if "error" in res:
            print("ERROR:", res["error"])
        else:
            for s in res.get("snippets", []):
                print(f"  - [{s.get('type')}] (Score: {s.get('score'):.4f}): {s.get('text')[:200]}...")

if __name__ == "__main__":
    test_cypher()
    test_vector()
