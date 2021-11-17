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


if [[ "${CI}" == "true" ]]; then
  magenta=
  yellow=
  green=
  clear_color=
fi


# Options.
current_service_file=./scripts/data/current_service


test_container() {
  local gate=${1}
  local service=${2}
  local version=${3}

  echo -e "${yellow}Building the images...${clear_color}"
  . scripts/util/build.sh "development" "${gate}" "${service}" "${version}"

  echo -e "${yellow}Executing tests for the ${gate} ${service} service...${clear_color}"
  docker run --rm --mount "type=bind,source=$(pwd)/temp,target=/data/" "khaleesi-ninja/${gate}/${service}" test
}


# Check if interactive mode.
services=("$@")
if [[ $# -eq 1 ]] && [[ "${1}" == "current_service" ]]; then
  if [[ ! -f "${current_service_file}" ]]; then
      . ./scripts/development/switch_current_service.sh
  fi
  while read -r raw_line; do
    IFS=":" read -r -a line <<< "${raw_line}"
    services=("${line[@]}")
  done <${current_service_file}
fi


echo -e "${magenta}Cleaning up old files and create mount directory...${clear_color}"
rm -r -f temp
mkdir temp

echo -e "${magenta}Updating the protos...${clear_color}"
. scripts/development/generate_protos.sh

echo -e "${magenta}Testing the services...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh test_container ${services[@]}

echo -e "${green}DONE! :D${clear_color}"
