#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
yellow='\033[0;33m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
gate=${1}
service=${2}
arguments=${6:-}


echo -e "${yellow}Cleaning up old files and create mount directory...${clear_color}"
rm -r -f temp
mkdir temp

echo -e "${yellow}Executing tests for the ${gate} ${service} service...${clear_color}"
docker run --rm --mount "type=bind,source=$(pwd)/temp,target=/data/" "khaleesi-ninja/${gate}/${service}:latest-development" test "${arguments}"

echo -e "${yellow}DONE testing! :D${clear_color}"
