UNWIND $rows AS row
MERGE (j:JobPosting {id: row.id})
SET j.title = row.title,
    j.level = row.level,
    j.salary_min = toInteger(row.salary_min),
    j.salary_max = toInteger(row.salary_max),
    j.status = row.status,
    j.posted_date = date(substring(row.posted_date, 0, 10)),
    j.remote_type = row.remote_type
