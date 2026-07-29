UNWIND $rows AS row
MERGE (c:Candidate {id: row.id})
SET c.name = row.name,
    c.years_experience = toInteger(row.years_experience),
    c.location = row.location,
    c.source = row.source
