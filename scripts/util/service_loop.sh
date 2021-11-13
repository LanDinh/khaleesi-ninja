#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
red='\033[0;31m'
clear_color='\033[0m'


# Options.
gate_services_file=./scripts/data/gate_services
function=${1}
input_gate=
input_service=
input_version=


if [[ $# -eq 1 ]]; then
  echo "No specific service was specified, so executing for all services..."
elif [[ $# -eq 4 ]]; then
  input_gate=${2}
  input_service=${3}
  input_version=${3}
  echo "${input_gate} ${input_service} version ${input_version} passed..."
else
  echo -e "${red}Wrong number of arguments to service-loop: $#!${clear_color}"
  exit 1
fi


# Read environments.
while read -r raw_line; do
  IFS=":" read -r -a line <<< "${raw_line}"
  gate="${line[0]}"
  service="${line[1]}"
  version="${line[2]}"

  if { [[ "${gate}" == "${input_gate}" ]] && [[ "${service}" == "${input_service}" ]]; } || [[ $# -eq 1 ]]; then
    echo -e "${magenta}Executing for the ${gate} ${service} version ${version}...${clear_color}"
    "${function}" "${gate}" "${service}" "${version}"
  fi
done <${gate_services_file}
