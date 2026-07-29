UNWIND $rows AS row
MERGE (r:Recruiter {id: row.id})
SET r.name = row.name,
    r.tenure_years = toInteger(row.tenure_years)
