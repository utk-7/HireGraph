UNWIND $rows AS row
MATCH (source:Employee {id: row.source_id})
MATCH (target:Department {id: row.target_id})
MERGE (source)-[:WORKS_IN]->(target)
