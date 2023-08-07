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


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
data_directory=./data
all_apps_file="${data_directory}/apps.json"
current_app_file="${data_directory}/current_app"


# Read apps.
apps=()
while read -r raw_line; do
  if [[ ${#raw_line} -eq 1 ]]; then
    continue
  fi
  apps+=("${raw_line}")
done <${all_apps_file}


# Helpers.
valid_option() {
  local input=$1
  local valid=false

  for app in "${apps[@]}"; do
    if [[ "${app}" == "${input}" ]]; then
      valid=true
      break
    fi
  done

  echo "${valid}"
}

echo -e "${magenta}Choose app:${clear_color}"
select input in "${apps[@]}"; do
  valid=$(valid_option "${input}")
  if [[ ${valid} == "true" ]]; then
    echo -e "${yellow}Writing '${input}' to temporary file...${clear_color}"
    rm -f "${current_app_file}"
    echo "${input}" > ${current_app_file}
    break
  else
    echo -e "${red}Invalid app chosen!${clear_color}"
  fi
done
