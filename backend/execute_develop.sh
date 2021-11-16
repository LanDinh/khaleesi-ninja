#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


magenta='\033[0;35m'
yellow='\033[0;33m'
red='\033[0;31m'
clear_color='\033[0m'


command=${1}


test() {
  return_code=0

  echo -e "${yellow}Django tests...${clear_color}"
  if ! python -m coverage run manage.py test; then
    return_code=1
  fi

  echo -e "${yellow}Copy coverage reports...${clear_color}"
  if ! mkdir -p /data/; then
    return_code=1
  fi
  if ! cp .coverage "/data/.coverage"; then
    return_code=1
  fi

  exit ${return_code}
}


run() {
  python manage.py grpcserver
}


source .venv/bin/activate

if [[ "${command}" == "test" ]]; then
  echo -e "${magenta}Execute tests...${clear_color}"
  test

elif [[ "${command}" == "run" ]]; then
  echo -e "${magenta}Running development server...${clear_color}"
  run

else
  echo -e "${red}Unsupported command ${command}!${clear_color}"
  exit 1
fi

