#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
yellow='\033[0;33m'
clear_color='\033[0m'


if [[ -z "${CI}" ]]; then
  yellow=
  clear_color=
fi


# Options.
gate_services_file=./scripts/data/gate_services
container_mode=${1}
gate=${2}
service=${3}
version=${4}
location="backend"
frontgate_version=


if [[ "${service}" == "frontgate" ]]; then
  location="frontgate"
elif [[ "${service}" == "backgate" ]]; then
  echo -e "${yellow}Fetching the frontgate version...${clear_color}"
  raw_frontgate=$(grep "^${gate}:frontgate:" "${gate_services_file}")
  IFS=":" read -r -a frontgate <<< "${raw_frontgate}"
  frontgate_version="${frontgate[2]}"
fi


echo -e "${yellow}Building the image khaleesi-ninja/${gate}/${service} for ${container_mode}...${clear_color}"
docker build "${location}" --build-arg gate="${gate}" --build-arg service="${service}" --build-arg version="${version}" --build-arg frontgate_version="${frontgate_version}" --target "${container_mode}" -t "khaleesi-ninja/${gate}/${service}:latest" -t "khaleesi-ninja/${gate}/${service}:${version}"

echo -e "${yellow}Cleaning up dangling images...${clear_color}"
docker image prune -f

echo -e "${yellow}DONE building the images! :D${clear_color}"
