UNWIND $rows AS row
MERGE (r:Review {id: row.id})
SET r.text = row.text,
    r.rating = toInteger(row.rating),
    r.review_date = datetime(row.review_date),
    r.review_type = row.review_type,
    r.recommends = CASE WHEN row.recommends = "" THEN null ELSE toBoolean(row.recommends) END
