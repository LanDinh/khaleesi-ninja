#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
green='\033[0;32m'
clear_color='\033[0m'


# Options.
deployment=${1}


echo -e "${magenta}Making sure the namespace exists...${clear_color}"
kubectl create namespace "khaleesi-ninja-${deployment}" --dry-run=client -o yaml | kubectl apply -f -


echo -e "${green}DONE! :D${clear_color}"
