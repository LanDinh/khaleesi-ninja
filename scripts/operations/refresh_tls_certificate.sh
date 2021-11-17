#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
yellow='\033[0;33m'
red='\033[0;31m'
clear_color='\033[0m'


if [[ "${CI}" == "true" ]]; then
  magenta=
  red=
  yellow=
  clear_color=
fi


# Options.
scripts_folder=scripts/util/refresh_tls_certificate
letsencrypt_folder="letsencrypt"
temp_folder="temp"
environments_file="./scripts/data/environments"
current_date=$(date +"%Y-%m-%d")
domain="khaleesi.ninja"
copy_in_command=
copy_out_command=

if [[ -z "${COPY_IN}" ]]; then
    copy_in_command="cp -aR \"${letsencrypt_folder}/live\"/'*' \"${temp_folder}/\""
else
    copy_in_command="${COPY_IN}"
fi
if [[ -z "${COPY_OUT}" ]]; then
    copy_out_command="cp -aR \"${temp_folder}\"/'*' \"${letsencrypt_folder}//\""
else
    copy_out_command="${COPY_OUT}"
fi


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


refresh_tls_certificate() {
  local environment=${1}
  local domain=${2}
  letsencrypt_certificate_folder="${letsencrypt_folder}/${current_date}/live/${domain}"

  echo -e "${yellow}Preparing certificate generation...${clear_color}"
  docker build ${scripts_folder} -t khaleesi-ninja/refresh_tls_certificate
  docker image prune -f

  echo -e "${yellow}Cleaning up old files and create mount directory...${clear_color}"
  rm -r -f ${temp_folder}
  mkdir ${temp_folder}
  # shellcheck disable=SC2086
  eval ${copy_in_command}

  echo -e "${yellow}Refreshing the certificate...${clear_color}"
  docker run --rm -it --mount "type=bind,source=$(pwd)/temp,target=/data/" --env KHALEESI_DOMAIN="${domain}" --env KHALEESI_EMAIL="${KHALEESI_EMAIL}" "khaleesi-ninja/refresh_tls_certificate"

  echo -e "${yellow}Backing up letsencrypt configuration...${clear_color}"
  mkdir -p "${letsencrypt_folder}/${current_date}"
  # shellcheck disable=SC2086
  eval ${copy_out_command}"${current_date}"

  echo -e "${yellow}Updating the kubernetes secret...${clear_color}"
  kubectl delete secret tls-certificate --ignore-not-found=true -n "khaleesi-ninja-${environment}"
  kubectl -n "khaleesi-ninja-${environment}" create secret tls tls-certificate --key "${letsencrypt_certificate_folder}/privkey.pem" --cert "${letsencrypt_certificate_folder}/fullchain.pem"
}


echo -e "${magenta}Choose environment:${clear_color}"
environments=()
while read -r raw_line; do
  environments+=("${raw_line}")
done <${environments_file}
select input in "${environments[@]}"; do
  valid=$(valid_option "${input}")
  if [[ ${valid} == "true" ]]; then
    if [[ ${input} != "production" ]]; then
      domain="${input}.khaleesi.ninja"
    fi
    echo -e "${magenta}Refreshing TLS certificate for '*.${domain}'...${clear_color}"
    refresh_tls_certificate "${input}" "${domain}"
    break
  else
    echo -e "${red}Invalid environment chosen!${clear_color}"
  fi
done
