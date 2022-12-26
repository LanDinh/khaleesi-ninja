#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
red='\033[0;31m'
yellow='\033[0;33m'
green='\033[0;32m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
current_service_file="./data/current_service"


# Check if interactive mode.
services=
if [[ ! -f "${current_service_file}" ]]; then
  . ./scripts/development/switch_current_service.sh
fi
while read -r raw_line; do
  read -r -a line <<< "$(./scripts/util/parse_service.sh "${raw_line}")"
  services=("${line[@]}")
done <${current_service_file}


make_migrations_container() {
  local gate=${1}
  local service=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  echo -e "${yellow}Building the images...${clear_color}"
  . scripts/util/build.sh "development" "${gate}" "${service}" "${type}" "${version}" "${deploy}"

  echo -e "${yellow}Making the migrations...${clear_color}"
  docker run --rm --mount "type=bind,source=$(pwd)/temp,target=/data/" "khaleesi-ninja/${gate}/${service}" make_migrations "microservice"

  echo -e "${yellow}Copying the migrations...${clear_color}"
  cp -r temp/* "backend/${gate}/${service}/microservice/migrations"
  rm -r "backend/${gate}/${service}/microservice/migrations/__pycache__"
}

echo -e "${magenta}Cleaning up old files and create mount directory...${clear_color}"
rm -r -f temp
mkdir temp

echo -e "${magenta}Making the migrations...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh make_migrations_container ${services[@]}

echo -e "${green}DONE! :D${clear_color}"
