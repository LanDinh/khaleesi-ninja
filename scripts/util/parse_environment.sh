#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Options.
line=${1}


# Parse the input.
IFS="\"" read -r -a split <<< "${line}"
environment="${split[3]}"
deploy="${split[7]}"
container_mode="${split[11]}"

echo "${environment}" "${deploy}" "${container_mode}"
