#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
green='\033[0;32m'
clear_color='\033[0m'


if [[ "${CI:-false}" == "true" ]]; then
  export TERM=xterm-color
fi


echo -e "${magenta}Deploying ingress...${clear_color}"
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.admissionWebhooks.enabled=false


echo -e "${magenta}Deploying kubegres...${clear_color}"
kubectl apply -f https://raw.githubusercontent.com/reactive-tech/kubegres/v1.16/kubegres.yaml

echo -e "${magenta}Deploying kube-prometheus...${clear_color}"
helm upgrade --install kube-prometheus kube-prometheus-stack \
  --repo https://prometheus-community.github.io/helm-charts \
  --namespace khaleesi-monitoring --create-namespace \
  --values kubernetes/configuration/third-party/kube-prometheus-stack.yml

echo -e "${magenta}Deploying cluster-wide resource...${clear_color}"
helm upgrade --install khaleesi-ninja kubernetes/khaleesi-ninja-cluster


echo -e "${green}DONE! :D${clear_color}"
