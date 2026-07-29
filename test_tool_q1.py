from chatbot_api.tools.cypher_tool import text_to_cypher_tool

res = text_to_cypher_tool("Which department has the longest average time-to-offer?")
print("Tool Result:", res)
