UNWIND $rows AS row
MERGE (a:Application {id: row.id})
SET a.applied_date = date(substring(row.applied_date, 0, 10)),
    a.current_stage = row.current_stage,
    a.status = row.status
