from chatbot_api.tools.cypher_tool import text_to_cypher_tool

questions = [
    "Which department has the longest average time-to-offer?",
    "How many candidates applied to Miller, Brennan and Berry?",
    "What is the average base salary for offers at Finance?",
    "Which recruiter has managed the most applications?",
    "How many employees are still employed vs. no longer employed?"
]

print("=======================================")
print("      TEXT-TO-CYPHER (GRAPH) TOOL      ")
print("=======================================\\n")

for i, q in enumerate(questions, 1):
    print(f"Q{i}: {q}")
    res = text_to_cypher_tool(q)
    print("CYPHER:")
    print(res.get("cypher", res.get("error")))
    print("RESULTS:")
    print(res.get("results"))
    print()
