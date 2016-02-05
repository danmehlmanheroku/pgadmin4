SELECT
    db.oid as did, db.datname as name, ta.spcname as spcname, db.datallowconn,
    has_database_privilege(db.oid, 'CREATE') as cancreate
FROM
    pg_database db
    LEFT OUTER JOIN pg_tablespace ta ON db.dattablespace = ta.oid
    {% if did %}WHERE db.oid={{did}}::int {% endif %}