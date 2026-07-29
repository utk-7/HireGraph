UNWIND $rows AS row
// Target can be JobPosting or Company
MATCH (source:Review {id: row.source_id})
MATCH (target {id: row.target_id}) WHERE target:JobPosting OR target:Company
MERGE (source)-[:ABOUT]->(target)
