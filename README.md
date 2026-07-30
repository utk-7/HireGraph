<div align="center">
  <h1>📈 HireGraph</h1>
  <p><strong>An advanced AI Recruitment & HR Analytics Assistant powered by Neo4j and LangGraph.</strong></p>

  [![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
  [![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
  [![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=flat&logo=neo4j&logoColor=white)](https://neo4j.com/)
  [![LangChain](https://img.shields.io/badge/LangChain-121212?style=flat)](https://langchain.com/)
</div>

<br>

**HireGraph** is an intelligent, agentic RAG (Retrieval-Augmented Generation) application designed to democratize HR data. It allows executives, recruiters, and HR analysts to ask natural language questions about candidates, interview experiences, turnover rates, and time-to-offer metrics, instantly translating those questions into complex Neo4j Cypher queries and vector searches.

## 📸 Screenshots

<div align="center">
  <img src="Screenshot 2026-07-31 042238.png" width="48%" alt="Streamlit Chat Interface" />
  <img src="/Screenshot 2026-07-31 042438.png" width="48%" alt="Render Deployment" />
</div>

---

## 🏗️ Architecture

HireGraph is split into three primary services and an evaluation harness:

1. **`chatbot_api/` (FastAPI + LangGraph Backend)**
   - The core intelligence engine. It uses a **LangGraph** routing agent to dynamically classify user questions.
   - **Structured Routing:** Translates analytical questions (e.g., *"What is the average time to offer in Sales?"*) into executable Cypher queries using a few-shot semantic retrieval system.
   - **Unstructured Routing:** Routes subjective queries (e.g., *"Summarize reviews for the engineering department"*) to a standard vector-based QA chain.
2. **`chatbot_frontend/` (Streamlit Chat UI)**
   - A sleek, responsive, and highly customized Streamlit application serving as the user interface.
   - Features dynamic Plotly charts (e.g., correlating Interview Ratings with Employee Turnover) and a built-in semantic cache for instant demo responses.
3. **`cypher_example_portal/` (Internal Knowledge Portal)**
   - A specialized internal tool allowing engineers to upload verified Question-to-Cypher examples directly into the Neo4j Vector Store. The LangGraph agent uses this vector index at runtime to ground its Cypher generation, drastically reducing syntax hallucinations.
4. **`evaluation/` (RAGAS Evaluation Harness)**
   - A fully automated evaluation pipeline that scores the agent's responses against a handcrafted "Gold Dataset" using **RAGAS** (Retrieval Augmented Generation Assessment). Measures Faithfulness, Answer Relevancy, and Context Precision.

---

## 🚀 Live Demo

- **Frontend (Streamlit Cloud):** [https://hiregraph-pyamfcvsewihjaappkenj7d.streamlit.app/](https://hiregraph-pyamfcvsewihjaappkenj7d.streamlit.app/)
- **Backend API (Render):** [https://hiregraph-api.onrender.com/docs](https://hiregraph-api.onrender.com/docs)

*(Note: To conserve LLM API quotas, the frontend includes a zero-call fallback cache. Clicking the suggested questions on the homepage will instantly yield perfect responses without consuming OpenRouter credits!)*

---

## 💻 Local Setup & Development

This project uses **Poetry** for dependency management.

### 1. Prerequisites
- Python 3.11+
- [Poetry](https://python-poetry.org/docs/#installation)
- A running Neo4j AuraDB instance
- An OpenRouter API Key (using `openai/gpt-oss-20b:free` or similar models)
- A HuggingFace API Token (for `all-MiniLM-L6-v2` embeddings)

### 2. Install Dependencies
```bash
# Install all dependencies (excluding dev by default)
poetry install
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY="your-openrouter-key"
NEO4J_URI="neo4j+s://your-db-id.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your-password"

NEO4J_CYPHER_EXAMPLES_INDEX_NAME="cypher_examples"
NEO4J_CYPHER_EXAMPLES_NODE_NAME="CypherExample"
NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY="question"
NEO4J_CYPHER_EXAMPLES_METADATA_NAME="cypher"

HOSPITAL_AGENT_MODEL="openai/gpt-oss-20b:free"
HOSPITAL_CYPHER_MODEL="openai/gpt-oss-20b:free"
HOSPITAL_QA_MODEL="openai/gpt-oss-20b:free"
```

### 4. Running the Services locally

**Run the API Backend:**
```bash
poetry run uvicorn chatbot_api.main:app --reload --port 8000
```

**Run the Streamlit Frontend:**
```bash
poetry run streamlit run chatbot_frontend/app.py
```

**Run the Internal Cypher Portal:**
```bash
poetry run streamlit run cypher_example_portal/app.py --server.port 8502
```

---

## 🐳 Docker Support

You can spin up the entire stack using Docker Compose.

```bash
docker-compose up --build
```
- API will be exposed on port `8000`
- Chat Frontend will be exposed on port `8501`
- Internal Cypher Portal will be exposed on port `8502`

---

## 🧪 Evaluation Harness

To run the RAGAS evaluation suite against the gold dataset (Note: This will consume LLM API calls):
```bash
# Run a dry-run (no LLM calls)
poetry run python evaluation/run_eval.py --dry-run

# Run the full evaluation suite
poetry run python evaluation/run_eval.py
```
The final evaluation metrics will be written to `evaluation/eval_results.json`.
