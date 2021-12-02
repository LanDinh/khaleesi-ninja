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
current_service_file="./data/current_service"


# Validate environment.
./scripts/util/valid_environment.sh "${1}"


# Check if interactive mode.
services=("${@:2}")
if [[ $# -eq 2 ]] && [[ "${2}" == "current_service" ]]; then
  if [[ ! -f "${current_service_file}" ]]; then
      . ./scripts/development/switch_current_service.sh
  fi
  while read -r raw_line; do
    read -r -a line <<< "$(./scripts/util/parse_service.sh "${raw_line}")"
    services=("${line[@]}")
  done <${current_service_file}
fi


deploy_service() {
  local gate=${1}
  local service=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  # Note: the order in which to call the values files is important!
  # Most specific first, to allow more generic ones to override some values
  # (e.g. only 1 replica for development)
  echo -e "${yellow}Deploying the service...${clear_color}"
  helm upgrade --install "khaleesi-ninja-${environment}-${gate}-${service}" kubernetes/khaleesi-ninja-service \
    --values "kubernetes/configuration/service/${gate}/${service}.yml" \
    --values "kubernetes/configuration/type/${type}.yml" \
    --values "kubernetes/configuration/gate/${gate}.yml" \
    --values "kubernetes/configuration/environment/${environment}.yml"

  if [[ "${environment}" == "development" ]] || [[ "${environment}" == "integration" ]]; then
    local container_mode=production
    if [[ "${environment}" == "development" ]]; then
      container_mode=development
    fi

    echo -e "${yellow}Rebuilding the container...${clear_color}"
    . scripts/util/build.sh "${container_mode}" "${gate}" "${service}" "${type}" "${version}" "${deploy}"

    echo -e "${yellow}Rolling out the new container...${clear_color}"
    kubectl rollout restart deployment "${gate}-${service}-deployment" -n "khaleesi-ninja-${environment}"
  fi
}

echo -e "${magenta}Deploying the services...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh deploy_service ${services[@]}


echo -e "${green}DONE! :D${clear_color}"
