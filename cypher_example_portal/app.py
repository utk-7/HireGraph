import os
import sys
import uuid

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from chatbot_api.tools.vector_tool import HFInferenceEmbeddings

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

st.set_page_config(page_title="Cypher Example Portal", layout="wide")

st.title("Cypher Example Portal")
st.markdown("""
**Note:** This portal has intentionally been left without authentication per PRD §7.4/§9, as it is meant for low-volume internal ad-hoc submissions by domain experts.
""")


def get_examples():
    if not NEO4J_URI:
        return []
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    except Exception:
        return []

    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (e:CypherExample) RETURN e.question AS question, e.cypherQuery AS query"
            )
            return [record.data() for record in result]
    except Exception:
        return []
    finally:
        driver.close()


def save_example(question, query):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    embeddings = HFInferenceEmbeddings()
    try:
        vector = embeddings.embed_query(question)
        with driver.session() as session:
            session.run(
                """
            CREATE (e:CypherExample {
                id: randomUUID(),
                question: $question,
                cypherQuery: $cypherQuery,
                embedding: $embedding
            })
            """,
                question=question,
                cypherQuery=query,
                embedding=vector,
            )
    finally:
        driver.close()


st.subheader("Submit New Example")
with st.form("new_example_form"):
    question = st.text_input("Natural Language Question")
    query = st.text_area("Correct Cypher Query")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not question or not query:
            st.error("Both fields are required.")
        else:
            with st.spinner("Generating embeddings and saving..."):
                try:
                    save_example(question, query)
                    st.success("Successfully saved to Neo4j vector store!")
                except Exception as e:
                    st.error(f"Failed to save: {str(e)}")

st.subheader("Existing Examples")
examples = get_examples()
if examples:
    st.dataframe(pd.DataFrame(examples), use_container_width=True)
else:
    st.info("No examples found in the database.")
