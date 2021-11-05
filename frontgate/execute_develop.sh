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

  echo -e "${yellow}React tests...${clear_color}"
  if ! npm run test; then
    return_code=1
  fi

  echo -e "${yellow}Copy coverage reports...${clear_color}"
  if ! mkdir -p /data/; then
    return_code=1
  fi
  if ! cp -a coverage "/data/coverage"; then
    return_code=1
  fi

  echo -e "${yellow}Eslint...${clear_color}"
  if ! npm run lint; then
    return_code=1
  fi

  exit ${return_code}
}

run() {
  npm run start
}

if [ "${command}" = "test" ]; then
  echo -e "${magenta}Execute tests...${clear_color}"
  test

elif [ "${command}" = "run" ]; then
  echo -e "${magenta}Run development server...${clear_color}"
  run

else
  echo -e "${red}Unsupported command ${command}!${clear_color}"
  exit 1
fi

