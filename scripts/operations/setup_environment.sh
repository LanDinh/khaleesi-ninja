#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
green='\033[0;32m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi

# Options.
environment=${1}


# Validate environment.
./scripts/util/valid_environment.sh "${1}"


echo -e "${magenta}Deploying the environment...${clear_color}"
helm upgrade --install "khaleesi-ninja-${environment}" kubernetes/khaleesi-ninja-environment \
  --values "kubernetes/configuration/environment/${environment}.yml"


if [[ "${CI:-false}" != "true" ]]; then
  echo -e "${magenta}Ensuring TLS certificates exist...${clear_color}"
  ./scripts/util/recreate_tls_certificate.sh "${environment}"
fi

echo -e "${magenta}Deploying the core gate...${clear_color}"
helm upgrade --install "khaleesi-ninja-${environment}-core" kubernetes/khaleesi-ninja-gate \
  --values "kubernetes/configuration/gate/core.yml" \
  --values "kubernetes/configuration/environment/${environment}.yml"


echo -e "${green}DONE! :D${clear_color}"
