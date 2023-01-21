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
version=${1}


echo -e "${yellow}Building the image khaleesi/base/backend-construction...${clear_color}"
DOCKER_BUILDKIT=1 docker buildx build backend -f backend/Dockerfile-base \
  --cache-to type=gha,mode=max \
  --cache-from type=gha \
  --build-context="pip_cache=$(pip cache dir)" \
  --target "construction" \
  -t "khaleesi/base/backend-construction:${version}"

echo -e "${yellow}Building the image khaleesi/base/backend-image...${clear_color}"
DOCKER_BUILDKIT=1 docker buildx build backend -f backend/Dockerfile-base \
  --cache-to type=gha,mode=max \
  --cache-from type=gha \
  --build-context="pip_cache=$(pip cache dir)" \
  --target "image" \
  -t "khaleesi/base/backend-image:${version}"

echo -e "${yellow}Cleaning up dangling images...${clear_color}"
docker image prune -f

echo -e "${yellow}DONE building the images! :D${clear_color}"
