#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
yellow='\033[0;33m'
clear_color='\033[0m'


# Options.
environment=${1}


build_container() {
  local gate=${1}
  local service=${2}
  local type=

  case $service in
    frontgate)
      type=frontgate
      ;;
    backgate)
      type=backgate
      ;;
    *)
      type=microservice
      ;;
    esac

  echo "Building the image khaleesi-ninja/${gate}/${service} for ${environment}...."
  docker build "${type}" --build-arg gate="${gate}" --target "${environment}" -t "khaleesi-ninja/${gate}/${service}"
}


echo -e "${yellow}Building the images...${clear_color}"
. scripts/service_loop.sh build_container "${@:2}"

echo -e "${yellow}Cleaning up dangling images...${clear_color}"
docker image prune -f

echo -e "${yellow}DONE building the images! :D${clear_color}"
