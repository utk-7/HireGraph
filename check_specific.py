import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('.env')
d = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD')))

query_extended = """
   MATCH (d:Department)-[:POSTED]->(jp:JobPosting)<-[:FOR_POSTING]-(a:Application)-[:RESULTED_IN]->(o:Offer)
   WHERE a.applied_date IS NOT NULL AND o.extended_date IS NOT NULL
   RETURN d.name AS department, 
          count(a) AS applications_with_offers,
          avg(duration.inDays(a.applied_date, o.extended_date).days) AS avg_days_to_offer
   ORDER BY avg_days_to_offer DESC
"""

with d.session() as s:
    for record in s.run(query_extended):
        print(f"{record['department']}: {record['applications_with_offers']} offers, {record['avg_days_to_offer']} days avg")




d.close()
