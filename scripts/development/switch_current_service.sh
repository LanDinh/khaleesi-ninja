#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
red='\033[0;31m'
yellow='\033[0;33m'
clear_color='\033[0m'


if [[ -z "${CI}" ]]; then
  magenta=
  red=
  yellow=
  clear_color=
fi


# Options.
scripts_data_directory=./scripts/data
gate_services_file="${scripts_data_directory}/gate_services"
current_service_file="${scripts_data_directory}/current_service"


# Read services.
services=()
while read -r raw_line; do
  services+=("${raw_line}")
done <${gate_services_file}


# Helpers.
valid_option() {
  local input=$1
  local valid=false

  for service in "${services[@]}"; do
    if [[ "${service}" == "${input}" ]]; then
      valid=true
      break
    fi
  done

  echo "${valid}"
}

echo -e "${magenta}Choose service:${clear_color}"
select input in "${services[@]}"; do
  valid=$(valid_option "${input}")
  if [[ ${valid} == "true" ]]; then
    echo -e "${yellow}Writing '${input}' to temporary file...${clear_color}"
    rm -f "${current_service_file}"
    echo "${input}" > ${current_service_file}
    break
  else
    echo -e "${red}Invalid service chosen!${clear_color}"
  fi
done
