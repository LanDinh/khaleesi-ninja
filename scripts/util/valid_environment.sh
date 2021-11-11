#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
red='\033[0;31m'
clear_color='\033[0m'


# Options.
input=${1}
environments_file="./scripts/data/environments"


# Read environments.
environments=()
while read -r raw_line; do
  environments+=("${raw_line}")
done <${environments_file}


# Check validity.
for environment in "${environments[@]}"; do
  if [[ "${environment}" == "${input}" ]]; then
    exit 0
  fi
done

echo -e "${red}Invalid environment '${input}'!${clear_color}"
exit 1
