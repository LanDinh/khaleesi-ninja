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
drop_database=false


# Validate environment.
./scripts/util/valid_environment.sh "${1}"


# Check if interactive mode.
services=("${@:2}")
if { [[ $# -eq 2 ]] || [[ $# -eq 3 ]]; } && [[ "${2}" == "current_service" ]]; then
  if [[ ! -f "${current_service_file}" ]]; then
      . ./scripts/development/switch_current_service.sh
  fi
  while read -r raw_line; do
    read -r -a line <<< "$(./scripts/util/parse_service.sh "${raw_line}")"
    services=("${line[@]}")
  done <${current_service_file}

  if [[ $# -eq 3 ]] && [[ "${3}" == "drop_database" ]]; then
    drop_database=true
  fi
fi


deploy_service() {
  local gate=${1}
  local service=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  if [[ ${deploy} == "false" ]]; then
    return 0
  fi

  if [[ "${environment}" == "development" ]] || [[ "${environment}" == "integration" ]]; then
    local container_mode=production
    if [[ "${environment}" == "development" ]]; then
      container_mode=development
    fi

    echo -e "${yellow}Rebuilding the container...${clear_color}"
    . scripts/util/build.sh "${container_mode}" "${gate}" "${service}" "${type}" "${version}" "${deploy}"
    sleep 5
  fi

  # Note: the order in which to call the values files is important!
  # Most specific first, to allow more generic ones to override some values
  # (e.g. only 1 replica for development)
  echo -e "${yellow}Deploying the service...${clear_color}"
  kubectl -n "khaleesi-ninja-${environment}" delete job "${gate}-${service}-kubegres-initialization" --ignore-not-found
  helm upgrade --install "khaleesi-ninja-${environment}-${gate}-${service}" kubernetes/khaleesi-ninja-service \
    --values "kubernetes/configuration/service/${gate}/${service}.yml" \
    --values "kubernetes/configuration/type/${type}.yml" \
    --values "kubernetes/configuration/gate/${gate}.yml" \
    --values "kubernetes/configuration/environment/${environment}.yml" \
    --set service.drop_database="${drop_database}"

  if [[ "${environment}" == "development" ]] || [[ "${environment}" == "integration" ]]; then
    echo -e "${yellow}Rolling out the new container...${clear_color}"
    kubectl -n "khaleesi-ninja-${environment}" rollout restart deployment "${gate}-${service}"

    wait_output=$(kubectl -n "khaleesi-ninja-${environment}" wait pod --all --for condition=ready --timeout 1m 2>&1) || true
    if [[ -n "${wait_output}" ]]; then
      grep -oE "[a-z]+-[a-z]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+" <<< "${wait_output}" | while read -r failed; do
        kubectl -n "khaleesi-ninja-${environment}" logs "${failed}" deployment || true
      done
    fi

    if [[ ${type} == "backgate" ]] || [[ ${type} == "micro" ]]; then
      echo -e "${yellow}Restarting grpcui...${clear_color}"
      kubectl -n "khaleesi-ninja-${environment}" rollout restart deployment "${gate}-${service}-grpcui"
    fi
  fi
}

echo -e "${magenta}Deploying the services...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/service_loop.sh deploy_service ${services[@]}

wait_output=$(kubectl -n "khaleesi-ninja-${environment}" wait pod --all --for condition=ready --timeout 1m 2>&1) || true
if [[ -n "${wait_output}" ]]; then
  grep -oE "[a-z]+-[a-z]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+" <<< "${wait_output}" | while read -r failed; do
    echo -e "${magenta}Logs for ${failed}...${clear_color}"
    kubectl -n "khaleesi-ninja-${environment}" logs "${failed}" deployment || true
  done
fi


echo -e "${green}DONE! :D${clear_color}"
