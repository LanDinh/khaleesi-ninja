#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
green='\033[0;32m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi

if [[ $# -eq 1 ]] && [[ "${1}" == "drop_database" ]]; then
  echo -e "${magenta}Dropping database...${clear_color}"
  dropdb --if-exists --force "${KHALEESI_DATABASE_NAME}"
fi


echo -e "${magenta}Creating users and database...${clear_color}"
psql -a -f /config/initialize-postgres.sql \
    -d postgres \
    -v superUser="${KHALEESI_DATABASE_SUPERUSER}" -v superUserPassword="${KHALEESI_DATABASE_SUPERUSER_PASSWORD}" \
    -v appUser="${KHALEESI_DATABASE_USER}" -v appUserPassword="${KHALEESI_DATABASE_PASSWORD}" \
    -v database="${KHALEESI_DATABASE_NAME}"


echo -e "${magenta}Asserting permissions...${clear_color}"
psql -a -f /config/initialize-database.sql \
    -d "${KHALEESI_DATABASE_NAME}" \
    -v appUser="${KHALEESI_DATABASE_USER}" \
    -v database="${KHALEESI_DATABASE_NAME}"

echo -e "${green}DONE! :D${clear_color}"
