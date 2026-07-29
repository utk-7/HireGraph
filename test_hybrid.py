import json
from chatbot_api.tools.hybrid_tool import hybrid_rag_tool

with open("data/generated/pattern_targets.json", "r") as f:
    targets = json.load(f)

attrition_ids = [t["cand_id"] for t in targets["attrition"]]
control_ids = [t["cand_id"] for t in targets["control"]]

q_flagship = f"""Find these exact candidates by ID, and then compare their employee tenure and later review sentiment:
Group A (Attrition): {', '.join(attrition_ids)}
Group B (Control): {', '.join(control_ids)}

Compare Group A vs Group B. Specifically, did Group A leave negative interview reviews before being hired and did they leave early?"""

print(">>> RUNNING HYBRID TOOL DIRECTLY <<<")
try:
    result = hybrid_rag_tool(q_flagship)
    with open("test_hybrid_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print("Done! Wrote to test_hybrid_results.json")
except Exception as e:
    print("Error:", e)
