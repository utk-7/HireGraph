import os, requests
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENROUTER_API_KEY')
res = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={'Authorization': f'Bearer {api_key}'},
    json={'model': 'openai/gpt-oss-20b:free', 'messages': [{'role': 'user', 'content': 'hi'}]}
)
print('Status:', res.status_code)
print('Response:', res.text)
