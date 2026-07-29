UNWIND $rows AS row
MATCH (source:Application {id: row.source_id})
MATCH (target:Recruiter {id: row.target_id})
MERGE (source)-[:MANAGED_BY]->(target)
