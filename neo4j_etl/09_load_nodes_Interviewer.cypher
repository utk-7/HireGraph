UNWIND $rows AS row
MERGE (i:Interviewer {id: row.id})
SET i.name = row.name,
    i.role = row.role,
    i.department = row.department
