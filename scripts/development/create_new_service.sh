#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
red='\033[0;31m'
yellow='\033[0;33m'
green='\033[0;32m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi

# Options.
symlink_frontgate_command=
symlink_backgate_command=
symlink_backend_command=


# Meta.

add_metadata() {
  local gate=${1}
  local service=${2}
  local type=${3}

  add_service_to_list_of_services "${gate}" "${service}" "${type}"
  add_kubernetes_manifest "${gate}" "${service}"
}

add_service_to_list_of_services() {
  local gate=${1}
  local service=${2}
  local type=${3}

  sed -i "1 a \ \ {\ \"gate\":\ \"${gate}\",\ \"name\":\ \"${service}\",\ \"type\":\ \"${type}\",\ \"version\":\ \"1.0.0\",\ \"deploy\":\ \"true\"\ }," data/services.json
}

add_kubernetes_manifest() {
  local gate=${1}
  local service=${2}

  mkdir -p "kubernetes/configuration/service/${gate}"
  sed "s/\${SERVICE}/${service}/g" "templates/kubernetes/service.yml" > "kubernetes/configuration/service/${gate}/${service}.yml"
}


# Backend.

create_backend() {
  local gate=${1}
  local service=${2}
  local type=${3}
  local project_folder="backend/${gate}/${service}"
  local template_folder="templates/backend"

  if [[ -z "${SYMLINK_BACKEND}" ]]; then
      symlink_backend_command="ln -nrs \"../../khaleesi\" \"backend/${gate}/${service}/khaleesi\""
  else
      symlink_backend_command="${SYMLINK_BACKEND}"
  fi

  echo -e "${yellow}Creating django project...${clear_color}"
  mkdir -p "$project_folder"
  python -m django startproject --template="${template_folder}/${type}_template" "${gate}_${service}" "${project_folder}"

  echo -e "${yellow}Adding symlinks...${clear_color}"
  # shellcheck disable=SC2086
  eval ${symlink_backend_command}

  echo -e "${yellow}Adding service to list of services...${clear_color}"
  add_metadata "${gate}" "${service}" "${type}"
}


create_micro() {
  local gate=${1}

  echo -e "${magenta}Enter service name:${clear_color}"
  read -r service

  create_backend "${gate}" "${service}" "micro"
}


create_backgate() {
  local gate=${1}

  if [[ -z "${SYMLINK_BACKGATE}" ]]; then
      symlink_backgate_command="ln -nrs \"../../core/backgate/core\" \"backend/${gate}/backgate/core\""
  else
      symlink_backgate_command="${SYMLINK_BACKGATE}"
  fi

  create_backend "${gate}" "backgate" "backgate"

  echo -e "${yellow}Adding backgate-specific symlinks...${clear_color}"
  # shellcheck disable=SC2086
  eval ${symlink_backgate_command}
}


# Frontgate.
create_frontgate() {
  local gate=${1}
  local project_folder="frontgate/${gate}"
  local template_folder="templates/frontgate"

  if [[ -z "${SYMLINK_FRONTGATE}" ]]; then
      symlink_frontgate_command="ln -nrs \"../../core/src/core\" \"frontgate/${gate}/src/core\""
  else
      symlink_frontgate_command="${SYMLINK_FRONTGATE}"
  fi

  echo -e "${yellow}Creating react project...${clear_color}"
  npx create-react-app "${project_folder}" --template "file:${template_folder}/cra-template-khaleesi-ninja-frontgate"

  echo -e "${yellow}Removing unnecessary files... (this might take a while)${clear_color}"
  rm "${project_folder}/.gitignore"
  rm "${project_folder}/package-lock.json"
  rm "${project_folder}/package.json"
  rm -r "${project_folder}/node_modules"

  echo -e "${yellow}Adding symlinks...${clear_color}"
  # shellcheck disable=SC2086
  eval ${symlink_frontgate_command}

  echo -e "${yellow}Adding service to list of services...${clear_color}"
  add_metadata "${gate}" "frontgate" "frontgate"
}


# Interactive user input.
echo -e "${magenta}Enter gate name:${clear_color}"
read -r gate

echo -e "${magenta}Enter service type:${clear_color}"
select input_type in gate micro; do
  case $input_type in
  gate)
    echo -e "${magenta}Creating gates...${clear_color}"
    create_frontgate "${gate}"
    create_backgate "${gate}"
    break
    ;;
  micro)
    echo -e "${magenta}Creating micro service...${clear_color}"
    create_micro "${gate}"
    break
    ;;
  *)
    echo -e "${red}Invalid service type"
    ;;
  esac
done

echo -e "${green}DONE! :D${clear_color}"
