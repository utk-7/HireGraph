import json
from chatbot_api.agent import invoke_agent

import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(10), wait=wait_exponential(multiplier=1, min=4, max=30))
def resilient_invoke(question):
    return invoke_agent(question)

def run_test(question: str):
    print("="*60)
    print(f"QUESTION: {question}")
    try:
        result = resilient_invoke(question)
    except Exception as e:
        print(f"Failed after retries: {e}")
        return
    
    messages = result.get("messages", [])
    
    # Extract tool chosen
    tool_calls = []
    for m in messages:
        if hasattr(m, 'tool_calls') and m.tool_calls:
            tool_calls.extend(m.tool_calls)
    
    if tool_calls:
        for msg in messages:
            if msg.type == "ai" and getattr(msg, "tool_calls", None):
                for tc in msg.tool_calls:
                    print(f"--> TOOL CHOSEN: {tc['name']}")
                    print(f"    Args: {json.dumps(tc['args'], indent=2)}")
            elif msg.type == "tool":
                print(f"    Tool Result: {msg.content[:500]}...")
    else:
        print("--> NO TOOL CHOSEN (Direct Answer)")
        
    final_answer = messages[-1].content
    try:
        print(f"\nFINAL ANSWER:\n{final_answer}\n")
    except UnicodeEncodeError:
        print(f"\nFINAL ANSWER:\n{final_answer.encode('ascii', 'replace').decode('ascii')}\n")

if __name__ == "__main__":
    # 3 Routing Tests
    q1 = "Which department has the longest average time-to-offer?"
    q2 = "What do candidates say about interviews for Software Engineer jobs?"
    q3 = "Summarize interview feedback from candidates rejected after 3+ rounds at Miller, Brennan and Berry"
    
    print(">>> SKIPPING ROUTING TESTS FOR SPEED <<<")
    # run_test(q1)
    # run_test(q2)
    # run_test(q3)
    
    q_hybrid = "What is the general interview sentiment of candidates who were hired but left within 6 months?"
    print(">>> RUNNING LIVE HYBRID AGENT TRACE <<<")
    run_test(q_hybrid)
