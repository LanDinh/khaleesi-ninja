#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
green='\033[0;32m'
yellow='\033[0;33m'
clear_color='\033[0m'


# Options.
environment=${1}
current_service_file="./scripts/data/current_service"


# Validate environment.
./scripts/util/valid_environment.sh "${1}"
namespace="khaleesi-ninja-${environment}"


# Check if interactive mode.
services=("${@:2}")
if [[ $# -eq 2 ]] && [[ "${2}" == "current_service" ]]; then
  if [ ! -f "${current_service_file}" ]; then
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

  echo -e "${yellow}Applying the manifests...${clear_color}"
  kubectl apply -k "kubernetes/environment/${environment}/${gate}-${service}" -n "${namespace}"

  if [ "${environment}" = "development" ]; then
    echo -e "${yellow}Rebuilding container...${clear_color}"
    . scripts/util/build.sh "development" "${gate}" "${service}"

    echo -e "${yellow}Rollout container...${clear_color}"
    # shellcheck disable=SC2068
    kubectl rollout restart deployment "${gate}-${service}-deployment" -n "${namespace}"

  elif [ "${environment}" = "staging" ]; then
    echo -e "${yellow}Rebuilding container...${clear_color}"
    . scripts/util/build.sh "production" "${gate}" "${service}"

    echo -e "${yellow}Rollout container...${clear_color}"
    # shellcheck disable=SC2068
    kubectl rollout restart deployment "${gate}-${service}-deployment" -n "${namespace}"
  fi
}


echo -e "${magenta}Installing the infrastructure...${clear_color}"
helm upgrade --install khaleesi-ninja-infrastructure kubernetes/khaleesi-ninja-infrastructure --set environment="${environment}"

echo -e "${magenta}Rollout the service...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh deploy_service ${services[@]}


echo -e "${green}DONE! :D${clear_color}"
