#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
red='\033[0;31m'
clear_color='\033[0m'


# Options.
function=${1}
gate_services_file=./scripts/data/gate_services


if [ $# -eq 1 ]; then
  echo "No specific service was specified, so executing for all services..."
  while read -r raw_line; do
    IFS="." read -r -a line <<< "${raw_line}"
    gate="${line[0]}"
    service="${line[1]}"
    echo "Executing for the ${gate} ${service} service..."
    "${function}" "${gate}" "${service}"
  done <${gate_services_file}

elif [ $# -eq 3 ]; then
  gate=${2}
  service=${3}
  ./scripts/util/valid_service.sh "${gate}" "${service}"
  echo "Executing for the ${gate} ${service} service..."
  "${function}" "${gate}" "${service}"
  
else
  echo -e "${red}Wrong number of arguments to service-loop: $#!${clear_color}"
  exit 1
fi
