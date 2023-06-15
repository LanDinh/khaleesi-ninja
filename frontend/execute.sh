#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


command=${1}


run() {
  npm run start
}


if [[ "${command}" == "run" ]]; then
  echo "Run server..."
  run

else
  echo "Unsupported command ${command}!"
  exit 1
fi

