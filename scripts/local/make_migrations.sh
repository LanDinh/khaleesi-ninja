#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
yellow='\033[0;33m'
green='\033[0;32m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
current_app_file="./data/current_app"
django_app=$1


# Check if interactive mode.
apps=
if [[ ! -f "${current_app_file}" ]]; then
  . ./scripts/local/switch_current_app.sh
fi
while read -r raw_line; do
  read -r -a line <<< "$(./scripts/util/parse_app.sh "${raw_line}")"
  apps=("${line[@]}")
done <${current_app_file}


make_migrations_container() {
  local site=${1}
  local app=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  echo -e "${yellow}Building the images...${clear_color}"
  . scripts/build.sh "${site}" "${app}" "${type}" "${version}" "${deploy}" "development"

  echo -e "${yellow}Making the migrations...${clear_color}"
  docker run --rm --mount "type=bind,source=$(pwd)/temp,target=/data/" "khaleesi-ninja/${site}/${app}:latest-development" make_migrations "${django_app}"

  echo -e "${yellow}Fixing metaclass issues in migrations...${clear_color}"
  sed -i '/bases=/d' temp/*.py

  echo -e "${yellow}Copying the migrations...${clear_color}"
  cp -r temp/* "backend/${site}/${app}/${django_app}/migrations"
  rm -r "backend/${site}/${app}/${django_app}/migrations/__pycache__"
}

echo -e "${magenta}Cleaning up old files and create mount directory...${clear_color}"
rm -r -f temp
mkdir temp

echo -e "${magenta}Making the migrations...${clear_color}"
# shellcheck disable=SC2068
make_migrations_container ${apps[@]}

echo -e "${green}DONE! :D${clear_color}"
