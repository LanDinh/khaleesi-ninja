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

  echo -e "${yellow}Building the image khaleesi-ninja/${gate}/${service} for ${environment}....${clear_color}"
  docker build "${type}" --build-arg gate="${gate}" --target "${environment}" -t "khaleesi-ninja/${gate}/${service}"
}


echo -e "${magenta}Building the images...${clear_color}"
. scripts/service_loop.sh build_container "${@:2}"

echo -e "${magenta}Cleaning up dangling images...${clear_color}"
docker image prune -f

echo -e "${green}DONE! :D${clear_color}"
