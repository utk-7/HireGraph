UNWIND $rows AS row
MATCH (source:Application {id: row.source_id})
MATCH (target:Offer {id: row.target_id})
MERGE (source)-[:RESULTED_IN]->(target)
