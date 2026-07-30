import os
import sys
from dotenv import load_dotenv
from langchain_core.callbacks import FileCallbackHandler
from chatbot_api.agent import invoke_agent

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv()

def main():
    print("Testing Conversation Memory (Multi-turn)...")
    handler = FileCallbackHandler("trace.txt")
    
    q1 = "Which department has the longest average time-to-offer?"
    print(f"\nUser: {q1}")
    result1 = invoke_agent(q1, thread_id="test_mem_3", callbacks=[handler])
    print(f"Agent: {result1['messages'][-1].content}")
    
    q2 = "What about the Sales department specifically?"
    print(f"\nUser: {q2}")
    result2 = invoke_agent(q2, thread_id="test_mem_3", callbacks=[handler])
    print(f"Agent: {result2['messages'][-1].content}")
    
    handler.file.flush()
    handler.file.close()

if __name__ == "__main__":
    main()
