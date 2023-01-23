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


# Options.
environment=${1}


deploy_service() {
  local gate=${1}
  local service=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  echo -e "${yellow}Deploying the service...${clear_color}"
  ./scripts/deploy.sh "${gate}" "${service}" "${type}" "${version}" "${deploy}" "${environment}"
}

echo -e "${magenta}Uploading the images...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh deploy_service

echo -e "${green}DONE! :D${clear_color}"
