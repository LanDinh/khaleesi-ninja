#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
yellow='\033[0;33m'
red='\033[0;31m'
clear_color=


# Options.
scripts_directory=./scripts
temp_directory="${scripts_directory}/temp"
gate_services_file="${scripts_directory}/data/gate_services"
current_service_file="${temp_directory}/current_service"


# Read services.
services=("same as before")
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
  if [[ ${input} == "same as before" ]]; then
    echo -e "${yellow}Reusing the same service...${clear_color}"
    break
  elif [[ ${valid} == "true" ]]; then
    echo -e "${yellow}Writing to temporary file...${clear_color}"
    rm -f "${current_service_file}"
    mkdir -p ${temp_directory}
    echo "${input}" > ${current_service_file}
    break
  else
    echo -e "${red}Invalid service chosen!${clear_color}"
  fi
done
