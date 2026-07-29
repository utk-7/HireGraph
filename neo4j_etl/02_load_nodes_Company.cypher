UNWIND $rows AS row
MERGE (c:Company {id: row.id})
SET c.name = row.name,
    c.industry = row.industry,
    c.size = row.size,
    c.headquarters = row.headquarters,
    c.founded_year = toInteger(row.founded_year)
