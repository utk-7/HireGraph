UNWIND $rows AS row
MERGE (o:Offer {id: row.id})
SET o.base_salary = toInteger(row.base_salary),
    o.equity = toInteger(row.equity),
    o.bonus = toInteger(row.bonus),
    o.extended_date = date(substring(row.extended_date, 0, 10)),
    o.decision = row.decision,
    o.decision_date = date(substring(row.decision_date, 0, 10))
