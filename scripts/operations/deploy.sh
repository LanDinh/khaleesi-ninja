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


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
environment=${1}
current_service_file="./scripts/data/current_service"


# Validate environment.
./scripts/util/valid_environment.sh "${1}"


# Check if interactive mode.
services=("${@:2}")
if [[ $# -eq 2 ]] && [[ "${2}" == "current_service" ]]; then
  if [[ ! -f "${current_service_file}" ]]; then
      . ./scripts/development/switch_current_service.sh
  fi
  while read -r raw_line; do
    IFS=":" read -r -a line <<< "${raw_line}"
    services=("${line[@]}")
  done <${current_service_file}
fi


deploy_service() {
  local gate=${1}
  local service=${2}
  local version=${3}

  echo -e "${yellow}Deploying the service...${clear_color}"
  helm upgrade --install "khaleesi-ninja-${environment}-${gate}-${service}" kubernetes/khaleesi-ninja-service --set environment="${environment}" --set gate="${gate}" --set service="${service}" --set version="${version}"

  if [[ "${environment}" == "development" ]] || [[ "${environment}" == "integration" ]]; then
    local container_mode=production
    if [[ "${environment}" == "development" ]]; then
      container_mode=development
    fi

    echo -e "${yellow}Rebuilding the container...${clear_color}"
    . scripts/util/build.sh "${container_mode}" "${gate}" "${service}" "${version}"

    echo -e "${yellow}Rolling out the new container...${clear_color}"
    kubectl rollout restart deployment "${gate}-${service}-deployment" -n "khaleesi-ninja-${environment}"
  fi
}


echo -e "${magenta}Deploying the infrastructure...${clear_color}"
docker build "infrastructure/envoy" -t "khaleesi-ninja/infrastructure/envoy:latest"
helm upgrade --install "khaleesi-ninja-infrastructure-${environment}" kubernetes/khaleesi-ninja-infrastructure --set environment="${environment}"

if [[ "${environment}" == "development" ]] || [[ "${environment}" == "integration" ]]; then
  echo -e "${magenta}Updating the protos...${clear_color}"
  . scripts/development/generate_protos.sh
fi

echo -e "${magenta}Deploying the services...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh deploy_service ${services[@]}


echo -e "${green}DONE! :D${clear_color}"
