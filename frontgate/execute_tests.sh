#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


magenta='\033[0;35m'
clear_color='\033[0m'

return_code=0


cd "/code/frontgate/${KHALEESI_GATE}/"

echo -e "${magenta}React tests...${clear_color}"
if ! npm run test; then
  return_code=1
fi

echo -e "${magenta}Copy coverage reports...${clear_color}"
if ! mkdir -p /data/; then
  return_code=1
fi
if ! cp -r /coverage "/data/coverage"; then
  return_code=1
fi

echo -e "${magenta}Eslint...${clear_color}"
if ! npm run lint; then
  return_code=1
fi


exit ${return_code}
