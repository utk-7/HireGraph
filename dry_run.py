import json
from chatbot_api.agent import llm, system_message, tools
from langchain_core.messages import SystemMessage, HumanMessage

q_hybrid = "What is the general interview sentiment of candidates who were hired but left within 6 months?"

# Create dry run
print("="*60)
print("SYSTEM PROMPT:")
print(system_message)
print("\n" + "="*60)

print("\nTOOL SCHEMAS BOUND TO LLM:")
for tool in tools:
    print(f"\nTool Name: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Args Schema: {tool.args_schema.schema()}")
    
print("\n" + "="*60)
print("USER QUERY:")
print(q_hybrid)
