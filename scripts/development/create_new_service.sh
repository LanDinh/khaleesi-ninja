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


# Backgate.
create_backgate() {
  local gate=${1}
  local project_folder="backend/${gate}/backgate"
  local template_folder="templates/backend"

  echo -e "${yellow}Creating django project...${clear_color}"
  mkdir -p "$project_folder"
  python -m django startproject --template="${template_folder}/backgate_template" "${gate}_backgate" "${project_folder}"

  echo -e "${yellow}Adding symlinks...${clear_color}"
  # shellcheck disable=SC2086
  eval ${symlink_backend_command}
  # shellcheck disable=SC2086
  eval ${symlink_backgate_command}

  echo -e "${yellow}Adding service to list of services...${clear_color}"
  add_service_to_list_of_services "${gate}" "backgate" "backgate"
  add_kubernetes_manifest "${gate}" "backgate"
}


# Frontgate.
create_frontgate() {
  local gate=${1}
  local project_folder="frontgate/${gate}"
  local template_folder="templates/frontgate"

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
  add_service_to_list_of_services "${gate}" "frontgate" "frontgate"
  add_kubernetes_manifest "${gate}" "backgate"
}


# Interactive user input.
echo -e "${magenta}Enter gate name:${clear_color}"
read -r gate

if [[ -z "${SYMLINK_FRONTGATE}" ]]; then
    symlink_frontgate_command="ln -nrs \"../../core/src/core\" \"frontgate/${gate}/src/core\""
else
    symlink_frontgate_command="${SYMLINK_FRONTGATE}"
fi
if [[ -z "${SYMLINK_BACKGATE}" ]]; then
    symlink_backgate_command="ln -nrs \"../../core/backgate/core\" \"backend/${gate}/backgate/core\""
else
    symlink_backgate_command="${SYMLINK_BACKGATE}"
fi
if [[ -z "${SYMLINK_BACKEND}" ]]; then
    symlink_backend_command="ln -nrs \"../../khaleesi\" \"backend/${gate}/backgate/khaleesi\""
else
    symlink_backend_command="${SYMLINK_BACKEND}"
fi

echo -e "${magenta}Enter service type:${clear_color}"
select input_type in gate; do
  case $input_type in
  gate)
    echo -e "${magenta}Creating gates...${clear_color}"
    create_frontgate "${gate}"
    create_backgate "${gate}"
    break
    ;;
  *)
    echo -e "${red}Invalid service type"
    ;;
  esac
done

echo -e "${green}DONE! :D${clear_color}"
