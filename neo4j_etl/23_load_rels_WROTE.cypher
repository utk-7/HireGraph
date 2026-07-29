UNWIND $rows AS row
// Source can be Candidate or Employee
MATCH (source {id: row.source_id}) WHERE source:Candidate OR source:Employee
MATCH (target:Review {id: row.target_id})
MERGE (source)-[:WROTE]->(target)
