import json
import os
import argparse
import time

def load_gold_data():
    path = os.path.join(os.path.dirname(__file__), "gold_data", "dataset.json")
    with open(path, "r") as f:
        return json.load(f)

def run_evaluation(dry_run=False):
    dataset = load_gold_data()
    print(f"Loaded {len(dataset)} gold examples.")
    
    results = []
    
    for item in dataset:
        print(f"\nEvaluating Q: {item['question']}")
        
        if dry_run:
            print("[DRY RUN] Skipping live agent and LLM-based RAGAS scoring.")
            # Mock the agent response and RAGAS metrics
            result = {
                "id": item["id"],
                "question": item["question"],
                "expected_answer": item["expected_answer"],
                "actual_answer": item["expected_answer"] + " [Mocked]",
                "expected_tool": item["expected_tool"],
                "actual_tool": item["expected_tool"],
                "ragas_faithfulness": 0.95,
                "ragas_answer_relevancy": 0.98,
                "cypher_match": True if item["expected_cypher"] else None
            }
            time.sleep(0.5)
        else:
            # Here we would invoke the live chatbot API
            # from chatbot_api.agent import invoke_agent
            # ... and then run ragas evaluating metrics ...
            # For now, this is a stub for tomorrow's execution.
            print("Live evaluation mode is disabled until quota resets.")
            return
            
        results.append(result)
        
    print("\nEvaluation Complete.")
    
    # Save report
    report_path = os.path.join(os.path.dirname(__file__), "eval_report.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the RAGAS evaluation harness.")
    parser.add_argument("--dry-run", action="store_true", help="Run with mock data to avoid LLM calls.")
    args = parser.parse_args()
    
    run_evaluation(dry_run=args.dry_run)
