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
current_service_file="./data/current_service"


# Check if interactive mode.
services=("$@")
if [[ $# -eq 1 ]] && [[ "${1}" == "current_service" ]]; then
  if [[ ! -f "${current_service_file}" ]]; then
    . ./scripts/development/switch_current_service.sh
  fi
  while read -r raw_line; do
    read -r -a line <<< "$(./scripts/util/parse_service.sh "${raw_line}")"
    services=("${line[@]}")
  done <${current_service_file}
fi


test_container() {
  local gate=${1}
  local service=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  echo -e "${yellow}Building the images...${clear_color}"
  . scripts/util/build.sh "development" "${gate}" "${service}" "${type}" "${version}" "${deploy}"

  echo -e "${yellow}Executing tests for the ${gate} ${service} service...${clear_color}"
  docker run --rm --mount "type=bind,source=$(pwd)/temp,target=/data/" "khaleesi-ninja/${gate}/${service}" test "${arguments}"
}


echo -e "${magenta}Specify the test cases!${clear_color}"
read -r arguments

echo -e "${magenta}Cleaning up old files and create mount directory...${clear_color}"
rm -r -f temp
mkdir temp

echo -e "${magenta}Updating the protos...${clear_color}"
. scripts/development/generate_protos.sh

echo -e "${magenta}Testing the services...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh test_container ${services[@]}

echo -e "${green}DONE! :D${clear_color}"
