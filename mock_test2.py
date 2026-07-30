import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

load_dotenv()

def main():
    print('Setting up mocked LLM...', flush=True)
    import chatbot_api.tools.cypher_tool
    with patch('langchain_openai.ChatOpenAI') as MockChatOpenAI:
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = 'MATCH (o:Offer) WHERE o.decision_date IS NOT NULL RETURN o.decision_date LIMIT 1'
        mock_llm_instance.invoke.return_value = mock_response
        MockChatOpenAI.return_value = mock_llm_instance
        
        from chatbot_api.tools.cypher_tool import cypher_rag_tool
        
        bad_query = 'MATCH (o:Offer) RETURN o.offer_date LIMIT 1'
        print(f'Executing bad Cypher query: {bad_query}', flush=True)
        
        result = cypher_rag_tool.invoke(bad_query)
        
        print('\n--- FINAL TOOL OUTPUT ---', flush=True)
        print(result, flush=True)
        
        print('\n--- REPAIR LOOP VERIFICATION ---', flush=True)
        if mock_llm_instance.invoke.called:
            print('SUCCESS: The LLM repair loop was triggered!', flush=True)
            repair_prompt_sent = mock_llm_instance.invoke.call_args[0][0]
            print('\n--- PROMPT SENT TO REPAIR LLM ---', flush=True)
            print(repair_prompt_sent, flush=True)
        else:
            print('FAILURE: The LLM repair loop was NOT triggered.', flush=True)

if __name__ == '__main__':
    main()
