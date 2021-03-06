{% import 'catalog/ppas/macros/catalogs.sql' as CATALOGS %}
SELECT
    2 AS nsptyp,
    nsp.nspname AS name,
    nsp.oid,
    array_to_string(nsp.nspacl::text[], ', ') as acl,
    r.rolname AS namespaceowner, description,
    has_schema_privilege(nsp.oid, 'CREATE') AS can_create,
    CASE
    WHEN nspname LIKE E'pg\\_%' THEN true
    ELSE false END AS is_sys_object,
    (SELECT array_to_string(defaclacl::text[], ', ') FROM pg_default_acl WHERE defaclobjtype = 'deftblacl' AND defaclnamespace = nsp.oid) AS tblacl,
    (SELECT array_to_string(defaclacl::text[], ', ') FROM pg_default_acl WHERE defaclobjtype = 'defseqacl' AND defaclnamespace = nsp.oid) AS seqacl,
    (SELECT array_to_string(defaclacl::text[], ', ') FROM pg_default_acl WHERE defaclobjtype = 'deffuncacl' AND defaclnamespace = nsp.oid) AS funcacl,
    (SELECT array_to_string(defaclacl::text[], ', ') FROM pg_default_acl WHERE defaclobjtype = 'deftypeacl' AND defaclnamespace = nsp.oid) AS typeacl
FROM
    pg_namespace nsp
    LEFT OUTER JOIN pg_description des ON
        (des.objoid=nsp.oid AND des.classoid='pg_namespace'::regclass)
    LEFT JOIN pg_roles r ON (r.oid = nsp.nspowner)
WHERE
    {% if scid %}
    nsp.oid={{scid}}::int AND
    {% endif %}
    nsp.nspparent = 0 AND
    (
{{ CATALOGS.LIST('nsp') }}
    )
ORDER BY 1, nspname;
