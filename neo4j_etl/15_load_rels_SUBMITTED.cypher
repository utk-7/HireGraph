UNWIND $rows AS row
MATCH (source:Candidate {id: row.source_id})
MATCH (target:Application {id: row.target_id})
MERGE (source)-[:SUBMITTED]->(target)
