CREATE FUNCTION pg_temp.create_database(superUser text, superUserPassword text, database text) RETURNS VOID AS $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS dblink;
    PERFORM DBLINK_EXEC(
            FORMAT('host=127.0.0.1 dbname=postgres user=%I password=%L', superUser, superUserPassword),
            FORMAT('CREATE DATABASE %I', database));
EXCEPTION
    WHEN duplicate_database THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
END
$$ LANGUAGE plpgsql;


CREATE FUNCTION pg_temp.create_user(username text, password text) RETURNS VOID AS $$
BEGIN
    EXECUTE FORMAT('CREATE USER %I PASSWORD %L', username, password);
EXCEPTION
    WHEN duplicate_object THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
    WHEN duplicate_database THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
END
$$ LANGUAGE plpgsql;


-- noinspection SyntaxError,SqlSignature
SELECT pg_temp.create_database(:'superUser', :'superUserPassword', :'database');
-- noinspection SyntaxError,SqlSignature
SELECT pg_temp.create_user(:'appUser', :'appUserPassword');
