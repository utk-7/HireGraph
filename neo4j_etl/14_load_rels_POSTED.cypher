UNWIND $rows AS row
MATCH (source:Department {id: row.source_id})
MATCH (target:JobPosting {id: row.target_id})
MERGE (source)-[:POSTED]->(target)
