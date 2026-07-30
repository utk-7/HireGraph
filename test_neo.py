from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
import sys

print('Starting script...', file=sys.stderr)
load_dotenv()
URI = os.getenv('NEO4J_URI')
AUTH = (os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
print(f'URI: {URI}, USER: {os.getenv("NEO4J_USER")}', file=sys.stderr)

try:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        # Task 1 query
        query = '''
        MATCH (c:Candidate)-[:WROTE]->(r:Review),
              (c)-[:HIRED_AS]->(e:Employee)
        WHERE r.review_type = 'interview_experience' AND r.rating IS NOT NULL
        WITH 
          CASE 
            WHEN r.rating <= 2 THEN '1-2'
            WHEN r.rating = 3 THEN '3'
            WHEN r.rating >= 4 THEN '4-5'
          END as rating_bucket,
          e.tenure_months as tenure
        RETURN rating_bucket, avg(tenure) as avg_tenure, count(*) as count
        ORDER BY rating_bucket
        '''
        res = session.run(query)
        print("Correlation Query Results:")
        for rec in res:
            print(f"Bucket: {rec['rating_bucket']}, Avg Tenure: {rec['avg_tenure']:.1f}, Count: {rec['count']}")
    driver.close()
    print('Done', file=sys.stderr)
except Exception as e:
    print('Error:', e, file=sys.stderr)
