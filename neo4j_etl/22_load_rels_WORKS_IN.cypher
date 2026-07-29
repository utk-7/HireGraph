UNWIND $rows AS row
MATCH (source {id: row.source_id}) WHERE source:Employee OR source:Interviewer
MATCH (target:Department {id: row.target_id})
MERGE (source)-[:WORKS_IN]->(target)
