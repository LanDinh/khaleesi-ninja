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
symlink_frontend_command=
symlink_backend_command=


# Meta.

add_metadata() {
  local site=${1}
  local app=${2}
  local type=${3}

  add_app_to_list_of_apps "${site}" "${app}" "${type}"
  add_kubernetes_manifest "${site}" "${app}"
}

add_app_to_list_of_apps() {
  local site=${1}
  local app=${2}
  local type=${3}

  sed -i "1 a \ \ {\ \"site\":\ \"${site}\",\ \"name\":\ \"${app}\",\ \"type\":\ \"${type}\",\ \"version\":\ \"1.0.0\",\ \"deploy\":\ \"true\"\ }," data/apps.json
}

add_kubernetes_manifest() {
  local site=${1}
  local app=${2}

  mkdir -p "kubernetes/configuration/app/${site}"
  sed "s/\${APP}/${app}/g" "templates/kubernetes/app.yml" > "kubernetes/configuration/app/${site}/${app}.yml"
}


# Backend.

create_backend() {
  local site=${1}
  local app=${2}
  local type=${3}
  local project_folder="backend/${site}/${app}"
  local template_folder="templates/backend"

  if [[ -z "${SYMLINK_BACKEND}" ]]; then
      symlink_backend_command="ln -nrs \"../../khaleesi\" \"backend/${site}/${app}/khaleesi\""
  else
      symlink_backend_command="${SYMLINK_BACKEND}"
  fi

  echo -e "${yellow}Creating django project...${clear_color}"
  mkdir -p "$project_folder"
  python -m django startproject --template="${template_folder}/${type}_template" "${site}_${app}" "${project_folder}"

  echo -e "${yellow}Adding symlinks...${clear_color}"
  # shellcheck disable=SC2086
  eval ${symlink_backend_command}

  echo -e "${yellow}Adding app to list of apps...${clear_color}"
  add_metadata "${site}" "${app}" "${type}"
}


create_micro() {
  local site=${1}

  echo -e "${magenta}Enter app name:${clear_color}"
  read -r app

  create_backend "${site}" "${app}" "micro"
}


# Frontend.
create_frontend() {
  local site=${1}
  local project_folder="frontend/${site}"
  local template_folder="templates/frontend"

  if [[ -z "${SYMLINK_FRONTEND}" ]]; then
      symlink_frontend_command="ln -nrs \"../../core/src/core\" \"frontend/${site}/src/core\""
  else
      symlink_frontend_command="${SYMLINK_FRONTEND}"
  fi

  echo -e "${yellow}Creating react project...${clear_color}"
  npx create-remix "${project_folder}" --template "${template_folder}/frontend_template" --no-install --typescript

  echo -e "${yellow}Removing unnecessary files...${clear_color}"
  rm "${project_folder}/package.json"

  echo -e "${yellow}Adding symlinks...${clear_color}"
  # shellcheck disable=SC2086
  eval ${symlink_frontend_command}

  echo -e "${yellow}Adding app to list of apps...${clear_color}"
  add_metadata "${site}" "frontend" "frontend"
}


# Interactive user input.
echo -e "${magenta}Enter site name:${clear_color}"
read -r site

echo -e "${magenta}Enter app type:${clear_color}"
select input_type in site micro; do
  case $input_type in
  site)
    echo -e "${magenta}Creating sites...${clear_color}"
    create_frontend "${site}"
    break
    ;;
  micro)
    echo -e "${magenta}Creating micro app...${clear_color}"
    create_micro "${site}"
    break
    ;;
  *)
    echo -e "${red}Invalid app type${clear_color}"
    ;;
  esac
done

echo -e "${green}DONE! :D${clear_color}"
