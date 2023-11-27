#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
yellow='\033[0;33m'
red='\033[0;31m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


# Options.
site=${1}
app=${2}
type=${3}
deploy=${5}
environment=${6}
drop_database=${7:-false}
installed=true


# Validate environment.
./scripts/util/valid_environment.sh "${environment}"


if [[ ${deploy} == "false" ]]; then
  echo -e "${red}Skipping deployment for ${site}-${app}!${clear_color}"
  exit 0
fi

echo -e "${yellow}Checking if the app ${site}-${app} is already deployed...${clear_color}"
if ! helm status "khaleesi-ninja-${environment}-${site}-${app}"; then
  installed=false
fi


# Note: the order in which to call the values files is important!
# Environment last to allow develop to only have 1 replica, then less specific to more specific.
echo -e "${yellow}Deploying the app ${site}-${app}...${clear_color}"
kubectl -n "khaleesi-ninja-${environment}" delete job "${site}-${app}-kubegres-initialization" --ignore-not-found
helm upgrade --install "khaleesi-ninja-${environment}-${site}-${app}" kubernetes/khaleesi-ninja-app \
  --values "kubernetes/configuration/site/${site}.yml" \
  --values "kubernetes/configuration/type/${type}.yml" \
  --values "kubernetes/configuration/app/${site}/${app}.yml" \
  --values "kubernetes/configuration/environment/${environment}.yml" \
  --set app.drop_database="${drop_database}"

# If the release was already installed before, we need to rolling restart latest versions.
if [[ "${installed}" == "true" ]]; then
  if [[ "${environment}" == "development" ]] || [[ "${environment}" == "integration" ]]; then
    echo -e "${yellow}Rolling out the new container...${clear_color}"
    kubectl -n "khaleesi-ninja-${environment}" rollout restart deployment "${site}-${app}"

    wait_output=$(kubectl -n "khaleesi-ninja-${environment}" wait pod -l site="${site}",app="${app}",type="${type}" --for condition=ready --timeout 1m 2>&1 > /dev/null) || true
    if [[ -n "${wait_output}" ]]; then
      grep -oE "[a-z]+-[a-z]+-[a-zA-Z0-9]+-[a-zA-Z0-9]+" <<< "${wait_output}" | while read -r failed; do
        echo -e "${red}Pod ${failed} failed to start!${clear_color}"
        kubectl -n "khaleesi-ninja-${environment}" logs "${failed}" deployment || true
      done
    fi

    if [[ ${type} == "micro" ]]; then
      echo -e "${yellow}Restarting grpcui...${clear_color}"
      kubectl -n "khaleesi-ninja-${environment}" rollout restart deployment "${site}-${app}-grpcui"
    fi
  fi
fi

echo -e "${yellow}DONE deploying! :D${clear_color}"
