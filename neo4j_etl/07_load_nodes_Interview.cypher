UNWIND $rows AS row
MERGE (i:Interview {id: row.id})
SET i.round_number = toInteger(row.round_number),
    i.interview_type = row.interview_type,
    i.date = date(substring(row.date, 0, 10)),
    i.outcome = row.outcome
