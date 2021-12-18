CREATE FUNCTION pg_temp.create_users_and_database(
    superUser text, superUserPassword text,
    writeUser text, writePassword text,
    readUser text, readPassword text,
    database text
) RETURNS VOID AS $$
BEGIN
  CREATE EXTENSION IF NOT EXISTS dblink;

  EXECUTE FORMAT('CREATE USER %I PASSWORD %L', writeUser, writePassword);
  EXECUTE FORMAT('CREATE USER %I PASSWORD %L', readUser, readPassword);

  PERFORM DBLINK_EXEC(
      FORMAT('host=127.0.0.1 dbname=postgres user=%I password=%L', superUser, superUserPassword),
      FORMAT('CREATE DATABASE %I', database));

EXCEPTION
  WHEN duplicate_object THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
  WHEN duplicate_database THEN RAISE NOTICE '%, skipping', SQLERRM USING ERRCODE = SQLSTATE;
END
$$ LANGUAGE plpgsql;


-- noinspection SyntaxError
SELECT pg_temp.create_users_and_database(
    :'superUser', :'superUserPassword',
    :'writeUser', :'writePassword',
    :'readUser', :'readPassword',
    :'database'
);
