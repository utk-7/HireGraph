import os
os.environ['USE_HF_MOCK'] = '1'
import asyncio
from chatbot_api.main import chat, ChatRequest
import traceback

async def main():
    print('Starting test...')
    req = ChatRequest(message='What is highest recruiting company', session_id='123')
    try:
        print('Calling chat endpoint...')
        res = await chat(req)
        print('Result:', res)
    except Exception as e:
        print('Exception occurred:')
        traceback.print_exc()

asyncio.run(main())
