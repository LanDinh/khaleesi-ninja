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


# Options.
environment=${1}
current_service_file="./data/current_service"
drop_database=false
container_mode=production


# Validate environment.
./scripts/util/valid_environment.sh "${environment}"


# Check if interactive mode.
services=("${@:2}")
if { [[ $# -eq 2 ]] || [[ $# -eq 3 ]]; } && [[ "${2}" == "current_service" ]]; then
  if [[ ! -f "${current_service_file}" ]]; then
      . ./scripts/development/switch_current_service.sh
  fi
  while read -r raw_line; do
    read -r -a line <<< "$(./scripts/util/parse_service.sh "${raw_line}")"
    services=("${line[@]}")
  done <${current_service_file}

  if [[ $# -eq 3 ]] && [[ "${3}" == "drop_database" ]]; then
    drop_database=true
  fi
fi

if [[ "${environment}" == "development" ]]; then
  container_mode=development
fi


deploy_service() {
  local gate=${1}
  local service=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  echo -e "${yellow}Building the image...${clear_color}"
  . scripts/build.sh "${gate}" "${service}" "${type}" "${version}" "${deploy}" "${container_mode}"

  echo -e "${yellow}Deploying the service...${clear_color}"
  . scripts/deploy.sh "${gate}" "${service}" "${type}" "${version}" "${deploy}" "${environment}" "${drop_database}"


}

echo -e "${magenta}Deploying the services...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh deploy_service ${services[@]}


echo -e "${green}DONE! :D${clear_color}"
