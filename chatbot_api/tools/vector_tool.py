import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError
from langchain_core.embeddings import Embeddings
from neo4j import GraphDatabase
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


class HFInferenceEmbeddings(Embeddings):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.client = InferenceClient(token=HF_API_TOKEN)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=15),
        stop=stop_after_attempt(7),
        retry=retry_if_exception_type(
            (HfHubHTTPError, requests.exceptions.RequestException)
        ),
    )
    def _call_api(self, texts: List[str]) -> Any:
        # Use the official client's feature_extraction mapping
        result = self.client.feature_extraction(texts, model=self.model_name)
        # feature_extraction returns a numpy array-like list of floats
        return result

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # InferenceClient accepts a list of strings
        # It returns a 2D numpy array, convert to list of lists
        result = self._call_api(texts)
        if hasattr(result, "tolist"):
            return result.tolist()
        return result

    def embed_query(self, text: str) -> List[float]:
        # InferenceClient returns 1D or 2D depending on input,
        # but safely wrap in list and extract
        result = self._call_api([text])
        if hasattr(result, "tolist"):
            result = result.tolist()
        return result[0]


from langchain_core.tools import tool


@tool
def vector_rag_tool(semantic_search_query: str, top_k: int = 5) -> str:
    """
    Executes a semantic vector search across unstructured review text in the database.
    Use this when the query is asking for general opinions, feedback, or sentiment without needing to filter by specific graph entities.
    - semantic_search_query: A natural language string describing what to search for.
    """
    embeddings = HFInferenceEmbeddings()

    try:
        query_vector = embeddings.embed_query(semantic_search_query)
    except Exception as e:
        return f"Failed to embed query: {str(e)}"

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    cypher_query = """
    CALL db.index.vector.queryNodes('review_embeddings', $top_k, $query_vector)
    YIELD node AS review, score
    RETURN review.id AS id, review.text AS text, review.review_type AS type, score
    """

    try:
        with driver.session() as session:
            result = session.run(cypher_query, top_k=top_k, query_vector=query_vector)
            snippets = [record.data() for record in result]
            if not snippets:
                return f"No relevant reviews found for '{semantic_search_query}'."

            res_str = f"Found {len(snippets)} relevant reviews for '{semantic_search_query}':\n"
            for s in snippets:
                res_str += f"- Type: {s['type']}, Score: {s['score']:.2f}\n  Text: {s['text']}\n"
            return res_str
    except Exception as e:
        return f"Failed to query Neo4j: {str(e)}"
    finally:
        driver.close()
