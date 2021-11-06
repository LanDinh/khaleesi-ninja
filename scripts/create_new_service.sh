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


# Kubernetes.
replace_placeholders_in_file() {
  local file=${1}
  local placeholder=${2}
  local value=${3}

  sed -i "s/\${${placeholder}}/${value}/" "${file}"
}

copy_kubernetes_folder_with_placeholders() {
  local folder=${1}
  local gate=${2}
  local service=${3}

  local source="templates/kubernetes/${folder}/."
  local destination="kubernetes/${folder}/${gate}-${service}/"

  mkdir -p "${destination}"
  cp -a "${source}" "${destination}"

  for file in "${destination}"/*; do
    replace_placeholders_in_file "${file}" "GATE" "${gate}"
    replace_placeholders_in_file "${file}" "SERVICE" "${service}"
  done
}

create_kubernetes_manifests() {
  local gate=${1}
  local service=${2}

  echo "Creating files for service definition..."
  copy_kubernetes_folder_with_placeholders "service" "${gate}" "${service}"

  echo "Creating files for environment kustomizations..."
  while read -r environment; do
    copy_kubernetes_folder_with_placeholders "${environment}" "${gate}" "${service}"
  done < "./scripts/data/environments"
}


# Meta.
add_service_to_lists_of_service() {
  local gate=${1}
  local service=${2}

  sed -i "1 a ${gate}.${service}" scripts/data/gate_services
  sed -i "1 a \ \ {\"gate\": \"${gate}\", \"service\": \"${service}\"}," .github/data/services.json
}

create_service_infrastructure() {
  local gate=${1}
  local service=${2}

  echo -e "${yellow}Creating kubernetes manifests...${clear_color}"
  create_kubernetes_manifests "${gate}" "${service}"

  echo -e "${yellow}Adding service to list of services...${clear_color}"
  add_service_to_lists_of_service "${gate}" "${service}"
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

  create_service_infrastructure "${gate}" "frontgate"
}


# Interactive user input.
echo -e "${magenta}Enter gate name:${clear_color}"
read -r gate

echo -e "${magenta}Enter service type:${clear_color}"
select type in gate; do
  case $type in
  gate)
    echo -e "${magenta}Creating frontgate...${clear_color}"
    create_frontgate "${gate}"
    break
    ;;
  *)
    echo -e "${red}Invalid service type"
    ;;
  esac
done

echo -e "${green}DONE! :D${clear_color}"
