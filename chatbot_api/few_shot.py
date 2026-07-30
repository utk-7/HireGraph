from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.vectorstores import InMemoryVectorStore
from chatbot_api.tools.vector_tool import HFInferenceEmbeddings

# Define our verified examples from past phases
examples = [
    {
        "question": "What is the general interview sentiment of candidates who were hired but left within 6 months?",
        "query": "MATCH (c:Candidate)-[:WROTE]->(r:Review), (c)-[:HIRED_AS]->(e:Employee) WHERE r.review_type = 'interview_experience' AND r.rating IS NOT NULL RETURN r.rating as rating, avg(e.tenure_months) as avg_tenure, count(*) as count ORDER BY rating"
    },
    {
        "question": "How many candidates applied?",
        "query": "MATCH (c:Candidate) RETURN count(c)"
    },
    {
        "question": "Which department has the longest average time-to-offer?",
        "query": "MATCH (d:Department)<-[:WORKS_IN]-(e:Employee)<-[:HIRED_AS]-(c:Candidate)-[:SUBMITTED]->(a:Application)-[:RESULTED_IN]->(o:Offer) RETURN d.name, avg(duration.inDays(date(a.applied_date), date(o.offer_date)).days) as avg_days ORDER BY avg_days DESC LIMIT 1"
    },
    {
        "question": "What do candidates say about interviews for Software Engineer jobs?",
        "query": "MATCH (j:JobPosting)<-[:ABOUT]-(r:Review) WHERE j.title = 'Software Engineer' RETURN r.text LIMIT 5"
    },
    {
        "question": "Summarize interview feedback from candidates rejected after 3+ rounds at Miller, Brennan and Berry",
        "query": "MATCH (c:Company {name: 'Miller, Brennan and Berry'})-[:HAS_DEPARTMENT]->(d)-[:POSTED]->(j:JobPosting)<-[:FOR_POSTING]-(a:Application)-[:HAS_INTERVIEW]->(i:Interview) WITH a, count(i) as rounds WHERE rounds >= 3 AND a.status = 'rejected' MATCH (a)<-[:SUBMITTED]-(cand:Candidate)-[:WROTE]->(r:Review) RETURN r.text"
    }
]

# Initialize the embeddings model
embeddings = HFInferenceEmbeddings()

# Create the example selector using in-memory vector store
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    embeddings,
    InMemoryVectorStore,
    k=2
)

def get_few_shot_prompt(question: str) -> str:
    """
    Retrieves semantically similar Cypher examples based on the question.
    """
    try:
        similar_examples = example_selector.select_examples({"question": question})
    except Exception as e:
        print(f"Error fetching few-shot examples: {e}")
        return ""
    
    if not similar_examples:
        return ""
        
    prompt_addition = "\n\nHere are some examples of correctly formatted Cypher queries for similar past questions:\n"
    for ex in similar_examples:
        prompt_addition += f"- User Question: {ex['question']}\n  Cypher Query: `{ex['query']}`\n"
        
    return prompt_addition
