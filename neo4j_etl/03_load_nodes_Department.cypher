UNWIND $rows AS row
MERGE (d:Department {id: row.id})
SET d.name = row.name
