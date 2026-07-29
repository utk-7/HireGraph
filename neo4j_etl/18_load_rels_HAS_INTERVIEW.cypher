UNWIND $rows AS row
MATCH (source:Application {id: row.source_id})
MATCH (target:Interview {id: row.target_id})
MERGE (source)-[:HAS_INTERVIEW]->(target)
