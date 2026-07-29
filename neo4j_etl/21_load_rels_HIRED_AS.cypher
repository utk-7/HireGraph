UNWIND $rows AS row
MATCH (source:Candidate {id: row.source_id})
MATCH (target:Employee {id: row.target_id})
MERGE (source)-[:HIRED_AS]->(target)
