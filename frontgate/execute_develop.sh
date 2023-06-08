#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


command=${1}


test() {
  return_code=0

  echo "React tests..."
  if ! npm run test; then
    return_code=1
  fi

  echo "Copy coverage reports..."
  if ! mkdir -p /data/; then
    return_code=1
  fi
  if ! cp -a coverage "/data/coverage"; then
    return_code=1
  fi

  echo "Eslint..."
  if ! npm run lint; then
    return_code=1
  fi

  echo "Type check..."
  if ! npm run typecheck; then
    return_code=1
  fi

  exit ${return_code}
}

run() {
  npm run build
  npm run start
}


if [[ "${command}" == "test" ]]; then
  echo "Execute tests..."
  test

elif [[ "${command}" == "run" ]]; then
  echo "Run development server..."
  run

else
  echo "Unsupported command ${command}!"
  exit 1
fi

