#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


magenta='\033[0;35m'
red='\033[0;31m'
clear_color='\033[0m'


command=${1}


run() {
  exec python manage.py grpcserver --settings khaleesi.core.settings.production
}


source .venv/bin/activate

if [[ "${command}" == "run" ]]; then
  echo -e "${magenta}Running production server...${clear_color}"
  run

else
  echo -e "${red}Unsupported command ${command}!${clear_color}"
  exit 1
fi

