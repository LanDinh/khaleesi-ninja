#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
yellow='\033[0;33m'
green='\033[0;32m'
clear_color='\033[0m'


test_container() {
  local gate=${1}
  local service=${2}

  echo -e "${yellow}Executing tests for the ${gate} ${service} service....${clear_color}"
  docker run --rm --mount "type=bind,source=$(pwd)/temp,target=/data/" "khaleesi-ninja/${gate}/${service}" test
}

echo -e "${magenta}Clean up old files and create mount directory...${clear_color}"
rm -r -f temp
mkdir temp

echo -e "${magenta}Building the images...${clear_color}"
. scripts/build.sh development "$@"

echo -e "${magenta}Testing the services...${clear_color}"
. scripts/service_loop.sh test_container "$@"

echo -e "${green}DONE! :D${clear_color}"
