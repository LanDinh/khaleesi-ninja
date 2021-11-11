#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
red='\033[0;31m'
clear_color='\033[0m'


# Options.
input_gate=${1}
input_service=${2}
services_file="./scripts/data/gate_services"


# Read environments.
services=()
while read -r raw_line; do
  services+=("${raw_line}")
done <${services_file}


# Check validity.
for raw_service in "${services[@]}"; do
  IFS="." read -r -a parsed_service <<< "${raw_service}"
  gate="${parsed_service[0]}"
  service="${parsed_service[1]}"
  if [[ "${gate}" == "${input_gate}" ]] && [[ "${service}" == "${input_service}" ]]; then
    exit 0
  fi
done

echo -e "${red}Invalid service for gate '${input_gate}' and service name '${input_service}'!${clear_color}"
exit 1
