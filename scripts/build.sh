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
all_services_file=./data/services.json
gate=${1}
service=${2}
type=${3}
version=${4}
container_mode=${6}
location="backend"


if [[ "${type}" == "frontend" ]]; then
  location="frontend"
  cache="cache=./"
else
  cache="pip_cache=$(pip cache dir)"
fi


echo -e "${yellow}Building the image khaleesi-ninja/${gate}/${service} for ${container_mode}...${clear_color}"
DOCKER_BUILDKIT=1 docker buildx build "${location}" \
  --build-context="${cache}" \
  --build-arg gate="${gate}" \
  --build-arg service="${service}" \
  --build-arg version="${version}" \
  --target "${container_mode}" \
  -t "khaleesi-ninja/${gate}/${service}:latest-${container_mode}" \
  -t "khaleesi-ninja/${gate}/${service}:${version}-${container_mode}"

echo -e "${yellow}Cleaning up dangling images...${clear_color}"
docker image prune -f

echo -e "${yellow}DONE building the images! :D${clear_color}"
