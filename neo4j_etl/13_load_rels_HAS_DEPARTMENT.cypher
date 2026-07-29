UNWIND $rows AS row
MATCH (source:Company {id: row.source_id})
MATCH (target:Department {id: row.target_id})
MERGE (source)-[:HAS_DEPARTMENT]->(target)
