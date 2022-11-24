#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
yellow='\033[0;33m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
letsencrypt_certificate_folder="letsencrypt/live"
domain="khaleesi.ninja"
environment="${1}"


recreate_tls_certificate() {
  local environment=${1}
  local domain=${2}

  echo -e "${yellow}Updating the kubernetes secret...${clear_color}"
  kubectl delete secret tls-certificate --ignore-not-found=true -n "khaleesi-ninja-${environment}"
  kubectl -n "khaleesi-ninja-${environment}" create secret tls tls-certificate --key "${letsencrypt_certificate_folder}/${domain}/privkey.pem" --cert "${letsencrypt_certificate_folder}/${domain}/fullchain.pem"
}


./scripts/util/valid_environment.sh "${environment}"


if [[ ${environment} != "production" ]]; then
  domain="${environment}.khaleesi.ninja"
fi

echo -e "${magenta}Recreating TLS certificate for '*.${domain}'...${clear_color}"
recreate_tls_certificate "${environment}" "${domain}"
