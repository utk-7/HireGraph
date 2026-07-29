UNWIND $rows AS row
MATCH (source:Interview {id: row.source_id})
MATCH (target:Interviewer {id: row.target_id})
MERGE (source)-[:CONDUCTED_BY]->(target)
