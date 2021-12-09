CREATE FUNCTION pg_temp.assert_permissions(
  writeUser text, readUser text,
  database text
) RETURNS VOID AS $$
BEGIN
    EXECUTE FORMAT('DROP SCHEMA IF EXISTS public');
    EXECUTE FORMAT('CREATE SCHEMA IF NOT EXISTS khaleesi');

    EXECUTE FORMAT('GRANT CONNECT ON DATABASE %I TO %I', database, readUser);
    EXECUTE FORMAT('GRANT CONNECT ON DATABASE %I TO %I', database, writeUser);

    EXECUTE FORMAT('GRANT USAGE ON SCHEMA khaleesi TO %I', readUser);
    EXECUTE FORMAT('GRANT USAGE ON SCHEMA khaleesi TO %I', writeUser);

    EXECUTE FORMAT('ALTER DEFAULT PRIVILEGES IN SCHEMA khaleesi GRANT SELECT ON TABLES TO %I', readUser);
    EXECUTE FORMAT('ALTER DEFAULT PRIVILEGES IN SCHEMA khaleesi GRANT SELECT ON TABLES TO %I', writeUser);


    EXECUTE FORMAT('ALTER DEFAULT PRIVILEGES IN SCHEMA khaleesi GRANT INSERT ON TABLES TO %I', writeUser);
    EXECUTE FORMAT('ALTER DEFAULT PRIVILEGES IN SCHEMA khaleesi GRANT UPDATE ON TABLES TO %I', writeUser);
    EXECUTE FORMAT('ALTER DEFAULT PRIVILEGES IN SCHEMA khaleesi GRANT DELETE ON TABLES TO %I', writeUser);
    EXECUTE FORMAT('ALTER DEFAULT PRIVILEGES IN SCHEMA khaleesi GRANT REFERENCES ON TABLES TO %I', writeUser);

END
$$ LANGUAGE plpgsql;


SELECT pg_temp.assert_permissions(:'writeUser', :'readUser', :'database');
