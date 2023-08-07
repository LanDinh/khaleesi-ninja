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


# Options.
current_app_file="./data/current_app"


# Check if interactive mode.
apps=("$@")
arguments=
if [[ $# -eq 1 ]]; then
  if [[ "${1}" == "current_app" ]] || [[ "${1}" == "specific_test" ]]; then
    if [[ ! -f "${current_app_file}" ]]; then
      . ./scripts/development/switch_current_app.sh
    fi
    while read -r raw_line; do
      read -r -a line <<< "$(./scripts/util/parse_app.sh "${raw_line}")"
      apps=("${line[@]}")
    done <${current_app_file}
  fi

  if [[ "${1}" == "specific_test" ]]; then
    echo -e "${magenta}Specify the test cases!${clear_color}"
    read -r arguments
  fi
fi


test_container() {
  local site=${1}
  local app=${2}
  local type=${3}
  local version=${4}
  local deploy=${5}

  echo -e "${yellow}Building the image...${clear_color}"
  . scripts/build.sh "${site}" "${app}" "${type}" "${version}" "${deploy}" "development"

  echo -e "${yellow}Testing the app...${clear_color}"
  . scripts/test.sh "${site}" "${app}" "${type}" "${version}" "${deploy}" "${arguments}"
}


echo -e "${magenta}Cleaning up old files and create mount directory...${clear_color}"
rm -r -f temp
mkdir temp

echo -e "${magenta}Updating the protos...${clear_color}"
. scripts/generate_protos.sh

echo -e "${magenta}Building the base images...${clear_color}"
. scripts/util/build-backend-base.sh 1.0.0 construction
. scripts/util/build-backend-base.sh 1.0.0 image

echo -e "${magenta}Testing the apps...${clear_color}"
# shellcheck disable=SC2068
. scripts/util/app_loop.sh test_container ${apps[@]}

echo -e "${green}DONE! :D${clear_color}"
