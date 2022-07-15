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

fixate_gate() {
  echo -e "${magenta}Enter gate name:${clear_color}"
  read -r gate
  # Replace all filters for the gate.
  sed -i -E "s#\\\\\"${gate}\\\\\"#\\\\\"{{ .Values.gate.name }}\\\\\"#g" "${file}"
  # Replace uid.
  sed -i -E "s#(\"uid\": \"\{\{ .Values.environment.name \}\}-)${gate}(.*\")#\1{{ .Values.gate.name }}\2#g" "${file}"
  # Replace title.
  sed -i -E "s#(\"title\": \")${gate}(.*\")#\1{{ .Values.gate.name }}\2#g" "${file}"
}

fixate_service() {
  echo -e "${magenta}Enter service name:${clear_color}"
  read -r service
  # Replace all filters for the service.
  sed -i -E "s#\\\\\"${service}\\\\\"#\\\\\"{{ .Values.service.name }}\\\\\"#g" "${file}"
  # Replace uid.
  sed -i -E "s#(\"uid\": \"\{\{ .Values.environment.name \}\}-\{\{ .Values.gate.name \}\}-)${service}(\")#\1{{ .Values.service.name }}\2#g" "${file}"
  # Replace title.
  sed -i -E "s#(\"title\": \"\{\{ .Values.gate.name \}\}-)${service}(\")#\1{{ .Values.service.name }}\2#g" "${file}"
}

# Interactive user input.
echo -e "${magenta}Enter dashboard type:${clear_color}"
select input_type in overview gate service; do
  case $input_type in
  overview)
    file=kubernetes/khaleesi-ninja-environment/data/grafana-dashboards/khaleesi-ninja.json
    adjust_grafana_dashboards "${file}"
    break
    ;;
  gate)
    file=kubernetes/khaleesi-ninja-gate/data/grafana-dashboards/gate.json
    adjust_grafana_dashboards "${file}"
    fixate_gate
    break
    ;;
  service)
    file=kubernetes/khaleesi-ninja-service/data/grafana-dashboards/service.json
    adjust_grafana_dashboards "${file}"
    fixate_gate
    fixate_service
    break
    ;;
  *)
    echo -e "${red}Invalid dashboard type${clear_color}"
    ;;
  esac
done

echo -e "${green}DONE! :D${clear_color}"
