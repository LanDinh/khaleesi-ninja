#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
red='\033[0;31m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
input=${1}
environments_file="./data/environments.json"


# Read environments.
environments=()
while read -r raw_line; do
  if [[ ${#raw_line} -eq 1 ]]; then
    continue
  fi
  IFS="\"" read -r -a line <<< "${raw_line}"
  environments+=("${line[3]}")
done <${environments_file}


# Check validity.
for environment in "${environments[@]}"; do
  if [[ "${environment}" == "${input}" ]]; then
    exit 0
  fi
done

echo -e "${red}Invalid environment '${input}'!${clear_color}"
exit 1
