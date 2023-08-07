#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
red='\033[0;31m'
green='\033[0;32m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


adjust_grafana_dashboards() {
echo -e "${magenta}Enter the environment:${clear_color}"
  select input_type in development integration staging production; do
    case $input_type in
    development)
      environment=development
      break
      ;;
    integration)
      environment=integration
      break
      ;;
    staging)
      environment=staging
      break
      ;;
    production)
      environment=production
      break
      ;;
    *)
      echo -e "${red}Invalid environment${clear_color}"
      ;;
    esac
  done
  # Escape legendFormat, since Grafana variables clash with helm variables.
  sed -i -E "s#(\"legendFormat\": \")([^\`]*)(\",)#\1{{\`\2\`}}\3#g" "${file}"
  # Remove id, as there can't be duplicates.
  sed -i -E "0,/.*\"id\".*/{s#(\"id\": )[0-9]*(,)#\1null\2#g}" "${file}"
  # Remove iteration, as it's not necessary without the id.
  sed -i -E "/iteration/d" "${file}"
  # Replace datasource selection.
  sed -i -E "0,/.*\"selected\"/{s#(\"selected\": )false(,)#\1true\2#g}" "${file}"
  sed -i -E "s#(\"khaleesi-ninja-)${environment}(\")#\1{{ .Values.environment.name }}\2#g" "${file}"
  sed -i -E "s#(\"uid\": \")prometheus\"#\1\${datasource}\"#g" "${file}"
  # Replace version.
  sed -i -E "s#\"version\": [0-9]*#\"version\": 1#g" "${file}"
  # Replace uid.
  sed -i -E "s#(\"uid\": \")${environment}(.*\")#\1{{ .Values.environment.name }}\2#g" "${file}"
}

fixate_site() {
  echo -e "${magenta}Enter site name:${clear_color}"
  read -r site
  # Replace all filters for the site.
  sed -i -E "s#\\\\\"${site}\\\\\"#\\\\\"{{ .Values.site.name }}\\\\\"#g" "${file}"
  # Replace uid.
  sed -i -E "s#(\"uid\": \"\{\{ .Values.environment.name \}\}-)${site}(.*\")#\1{{ .Values.site.name }}\2#g" "${file}"
  # Replace title.
  sed -i -E "s#(\"title\": \")${site}(.*\")#\1{{ .Values.site.name }}\2#g" "${file}"
}

fixate_app() {
  echo -e "${magenta}Enter app name:${clear_color}"
  read -r app
  # Replace all filters for the app.
  sed -i -E "s#\\\\\"${app}\\\\\"#\\\\\"{{ .Values.app.name }}\\\\\"#g" "${file}"
  # Replace uid.
  sed -i -E "s#(\"uid\": \"\{\{ .Values.environment.name \}\}-\{\{ .Values.site.name \}\}-)${app}(\")#\1{{ .Values.app.name }}\2#g" "${file}"
  # Replace title.
  sed -i -E "s#(\"title\": \"\{\{ .Values.site.name \}\}-)${app}(\")#\1{{ .Values.app.name }}\2#g" "${file}"
}

# Interactive user input.
echo -e "${magenta}Enter dashboard type:${clear_color}"
select input_type in overview site app; do
  case $input_type in
  overview)
    file=kubernetes/khaleesi-ninja-environment/data/grafana-dashboards/khaleesi-ninja.json
    adjust_grafana_dashboards "${file}"
    break
    ;;
  site)
    file=kubernetes/khaleesi-ninja-site/data/grafana-dashboards/site.json
    adjust_grafana_dashboards "${file}"
    fixate_site
    break
    ;;
  app)
    file=kubernetes/khaleesi-ninja-app/data/grafana-dashboards/app.json
    adjust_grafana_dashboards "${file}"
    fixate_site
    fixate_app
    break
    ;;
  *)
    echo -e "${red}Invalid dashboard type${clear_color}"
    ;;
  esac
done

echo -e "${green}DONE! :D${clear_color}"
