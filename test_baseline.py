from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
load_dotenv()
URI = os.getenv('NEO4J_URI')
AUTH = (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
driver = GraphDatabase.driver(URI, auth=AUTH)
with driver.session() as session:
    # Query for baseline
    query = '''
    MATCH (c:Candidate)-[:WROTE]->(r:Review), (c)-[:HIRED_AS]->(e:Employee)
    WHERE r.review_type = 'interview_experience' AND r.rating IS NOT NULL
    WITH count(r) as total_reviews, sum(CASE WHEN r.rating <= 2 THEN 1 ELSE 0 END) as low_rating_count
    RETURN total_reviews, low_rating_count, (toFloat(low_rating_count) / total_reviews) * 100 as percentage
    '''
    res = session.run(query)
    for rec in res:
        print(f"Total: {rec['total_reviews']}, Low Rating (1-2): {rec['low_rating_count']}, Percentage: {rec['percentage']:.2f}%")
driver.close()
