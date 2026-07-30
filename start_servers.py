import subprocess
import time
import os
import sys

def start():
    print("Starting FastAPI backend...")
    env = os.environ.copy()
    env["USE_HF_MOCK"] = "1"
    
    # Start FastAPI
    backend = subprocess.Popen(
        ["poetry", "run", "uvicorn", "chatbot_api.main:app", "--port", "8000"],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    print("Starting Streamlit frontend...")
    # Start Streamlit
    frontend = subprocess.Popen(
        ["poetry", "run", "streamlit", "run", "chatbot_frontend/app.py", "--server.port", "8501", "--server.headless", "true"],
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    start()
