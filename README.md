# HireGraph

HireGraph is an enterprise-grade AI chatbot that performs Graph+Vector RAG (Retrieval-Augmented Generation) on recruiting and human resources data. 

*(Demo GIF will be added here once live LLM verification completes)*

## Architecture

HireGraph leverages a **Hybrid Knowledge Graph (Neo4j)** and **Vector Search** to answer complex analytical and qualitative questions:
- **FastAPI Backend (`chatbot_api/`)**: Hosts a LangGraph-powered ReAct agent that routes user queries to the correct specialized tool:
  - **Graph Cypher Tool**: Translates natural language into Cypher queries using few-shot grounding to query hard numbers and multi-hop relationships (e.g., time-to-offer averages, attrition rates).
  - **Vector Search Tool**: Uses HuggingFace embeddings (`all-MiniLM-L6-v2`) and Neo4j vector indexing to perform semantic search over unstructured interview feedback and candidate reviews.
  - **Hybrid Capabilities**: Can seamlessly route between structured nodes (Candidates, Employees, Applications) and unstructured vectors (Reviews).
- **Streamlit Frontend (`chatbot_frontend/`)**: Provides a beautiful, themed conversational UI with chat memory, rate limit handling, and inline data visualization (e.g., Plotly Attrition charts).
- **Cypher Example Portal (`cypher_example_portal/`)**: An admin tool (local-only) that allows domain experts to submit custom Cypher examples directly into the Neo4j vector index to continuously train and ground the Text-to-Cypher agent via few-shot learning.

## Setup & Local Development

### Requirements
- Python 3.11
- Poetry
- A running Neo4j instance (AuraDB or local)
- OpenRouter API Key (for the LLM)
- HuggingFace API Token (for embeddings)

### Environment Variables
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_key
HF_API_TOKEN=your_token
NEO4J_URI=bolt://your_neo4j_uri
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Running Locally
You can run all services using Docker Compose:
```bash
docker-compose up --build
```
Or run them locally via Poetry:
```bash
poetry install
poetry run python start_servers.py
```

- **Frontend Chat**: `http://localhost:8501`
- **FastAPI Backend**: `http://localhost:8000`
- **Cypher Example Portal**: `http://localhost:8502` (if started manually via `poetry run streamlit run cypher_example_portal/app.py`)

## Evaluation Harness
An automated evaluation harness (using RAGAS) is available in `evaluation/`. It measures faithfulness, answer relevancy, and Cypher precision against a curated gold dataset.
```bash
poetry run python evaluation/run_eval.py
```
