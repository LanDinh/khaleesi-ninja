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
all_app_file=./data/apps.json
function=${1}
input_site=
input_app=
input_type=
input_version=


if [[ $# -eq 1 ]]; then
  echo "No specific app was specified, so executing for all apps..."
elif [[ $# -eq 6 ]]; then
  input_site=${2}
  input_app=${3}
  input_type=${4}
  input_version=${5}
  echo "${input_site} ${input_app} of type ${input_type} v${input_version} passed..."
else
  echo -e "${red}Wrong number of arguments to app-loop: $#!${clear_color}"
  exit 1
fi


# Read environments.
while read -r raw_line; do
  if [[ ${#raw_line} -eq 1 ]]; then
    continue
  fi
  read -r -a line <<< "$(./scripts/util/parse_app.sh "${raw_line}")"
  site="${line[0]}"
  app="${line[1]}"
  type="${line[2]}"
  version="${line[3]}"
  deploy="${line[4]}"

  if { [[ "${site}" == "${input_site}" ]] && [[ "${app}" == "${input_app}" ]]; } || [[ $# -eq 1 ]]; then
    echo -e "${magenta}Executing for the ${site} ${app} of type ${type} v${version}...${clear_color}"
    "${function}" "${site}" "${app}" "${type}" "${version}" "${deploy}"
  fi
done <${all_app_file}
