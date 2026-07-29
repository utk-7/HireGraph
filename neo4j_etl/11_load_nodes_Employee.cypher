UNWIND $rows AS row
MERGE (e:Employee {id: row.id})
SET e.name = row.name,
    e.title = row.title,
    e.department = row.department,
    e.hire_date = date(substring(row.hire_date, 0, 10)),
    e.tenure_months = toInteger(row.tenure_months),
    e.still_employed = toBoolean(row.still_employed),
    e.converted_from_candidate = toBoolean(row.converted_from_candidate)
