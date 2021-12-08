CREATE FUNCTION pg_temp.install_extensions() RETURNS VOID AS $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS dblink;
END
$$ LANGUAGE plpgsql;


CREATE FUNCTION pg_temp.create_users(
    writeUser text, writePassword text,
    readUser text, readPassword text
) RETURNS VOID AS $$
BEGIN
    EXECUTE FORMAT('CREATE USER %I PASSWORD %L', writeUser, writePassword);
    EXECUTE FORMAT('CREATE USER %I PASSWORD %L', readUser, readPassword);

EXCEPTION
    WHEN duplicate_object THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
END
$$ LANGUAGE plpgsql;


CREATE FUNCTION pg_temp.create_database(
    superUser text, superUserPassword text,
    writeUser text, readUser text,
    database text
) RETURNS VOID AS $$
BEGIN
    PERFORM DBLINK_EXEC(
            FORMAT('host=127.0.0.1 dbname=postgres user=%I password=%L', superUser, superUserPassword),
            FORMAT('CREATE DATABASE %I OWNER %I', database, writeUser));
    EXECUTE FORMAT('ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO %I', readUser);

EXCEPTION
    WHEN duplicate_database THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
END
$$ LANGUAGE plpgsql;


SELECT pg_temp.install_extensions();
SELECT pg_temp.create_users(
  :'writeUser', :'writePassword',
  :'readUser', :'readPassword'
);
SELECT pg_temp.create_database(
  :'superUser', :'superUserPassword',
  :'writeUser', :'readUser',
  :'database'
);
