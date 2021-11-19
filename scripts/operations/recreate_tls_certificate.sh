#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
red='\033[0;31m'
yellow='\033[0;33m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
letsencrypt_certificate_folder="letsencrypt/live/live"
environments_file="./scripts/data/environments"
domain="khaleesi.ninja"
environment=


# Helpers.
valid_option() {
  local input=$1
  local valid=false

  for environment in "${environments[@]}"; do
    if [[ "${environment}" == "${input}" ]]; then
      valid=true
      break
    fi
  done

  echo "${valid}"
}


recreate_tls_certificate() {
  local environment=${1}
  local domain=${2}

  echo -e "${yellow}Updating the kubernetes secret...${clear_color}"
  kubectl delete secret tls-certificate --ignore-not-found=true -n "khaleesi-ninja-${environment}"
  kubectl -n "khaleesi-ninja-${environment}" create secret tls tls-certificate --key "${letsencrypt_certificate_folder}/${domain}/privkey.pem" --cert "${letsencrypt_certificate_folder}/${domain}/fullchain.pem"
}


if [[ $# -eq 1 ]]; then
  environment=${1}
  ./scripts/util/valid_environment.sh "${environment}"
else
  echo -e "${magenta}Choose environment:${clear_color}"
  environments=()
  while read -r raw_line; do
    environments+=("${raw_line}")
  done <${environments_file}
  select input in "${environments[@]}"; do
    valid=$(valid_option "${input}")
    if [[ ${valid} == "true" ]]; then
      break
    else
      echo -e "${red}Invalid environment chosen!${clear_color}"
    fi
  done
fi

if [[ ${input} != "production" ]]; then
  domain="${input}.khaleesi.ninja"
fi

echo -e "${magenta}Recreating TLS certificate for '*.${domain}'...${clear_color}"
recreate_tls_certificate "${input}" "${domain}"
