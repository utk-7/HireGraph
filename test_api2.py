from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

load_dotenv()
try:
    llm = ChatOpenAI(
        base_url='https://openrouter.ai/api/v1',
        api_key=os.getenv('OPENROUTER_API_KEY'),
        model='openai/gpt-oss-20b:free',
        temperature=0,
        max_retries=0
    )
    res = llm.invoke('Hi, reply with exactly the word SUCCESS')
    with open('api_status.txt', 'w') as f:
        f.write(res.content)
except Exception as e:
    with open('api_status.txt', 'w') as f:
        f.write(str(e))
