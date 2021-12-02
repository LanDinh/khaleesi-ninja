#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
red='\033[0;31m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
all_services_file=./data/services.json
function=${1}
input_gate=
input_service=
input_type=
input_version=
input_deploy=


if [[ $# -eq 1 ]]; then
  echo "No specific service was specified, so executing for all services..."
elif [[ $# -eq 6 ]]; then
  input_gate=${2}
  input_service=${3}
  input_type=${4}
  input_version=${5}
  input_deploy=${6}
  echo "${input_gate} ${input_service} of type ${input_type} v${input_version} passed..."
else
  echo -e "${red}Wrong number of arguments to service-loop: $#!${clear_color}"
  exit 1
fi


# Read environments.
while read -r raw_line; do
  if [[ ${#raw_line} -eq 1 ]]; then
    continue
  fi
  read -r -a line <<< "$(./scripts/util/parse_service.sh "${raw_line}")"
  gate="${line[0]}"
  service="${line[1]}"
  type="${line[2]}"
  version="${line[3]}"
  deploy="${line[4]}"

  if { [[ "${gate}" == "${input_gate}" ]] && [[ "${service}" == "${input_service}" ]]; } || [[ $# -eq 1 ]]; then
    echo -e "${magenta}Executing for the ${gate} ${service} of type ${type} v${version}...${clear_color}"
    "${function}" "${gate}" "${service}" "${type}" "${version}" "${deploy}"
  fi
done <${all_services_file}
