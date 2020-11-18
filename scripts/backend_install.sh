#!/bin/bash

set -e
set -o pipefail

# Fix Postgres, since Travis messes up its ports.
sudo apt-get update
sudo apt-get --yes remove postgresql\*
sudo apt-get install --yes postgresql-12 postgresql-client-12
sudo sed -i 's/port = 5433/port = 5432/' /etc/postgresql/*/main/postgresql.conf
sudo cp /etc/postgresql/{10,12}/main/pg_hba.conf
sudo service postgresql restart 12

# Install dependencies.
pip install -r backend/requirements.txt

# Prepare the Postgres database.
psql -U postgres -c "CREATE EXTENSION citext" -d template1
psql -U postgres -c "CREATE USER khaleesi_ninja;"
psql -U postgres -c "ALTER USER khaleesi_ninja CREATEDB;"
psql -U postgres -c "CREATE DATABASE khaleesi_ninja OWNER khaleesi_ninja;"

# Prepare Python.
PYTHONPATH=${PYTHONPATH}:$(pwd)/backend
export PYTHONPATH
python backend/base/manage.py makemigrations
python backend/base/manage.py migrate
