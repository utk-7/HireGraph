UNWIND $rows AS row
MATCH (source:Application {id: row.source_id})
MATCH (target:JobPosting {id: row.target_id})
MERGE (source)-[:FOR_POSTING]->(target)
