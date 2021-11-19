#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


command=${1}


test() {
  return_code=0

  echo "Django tests..."
  if ! python -m coverage run manage.py test; then
    return_code=1
  fi

  echo "Copy coverage reports..."
  if ! mkdir -p /data/coverage; then
    return_code=1
  fi
  if ! cp -a .coverage "/data/coverage/.coverage"; then
    return_code=1
  fi

  echo "Mypy..."
  if ! python -m mypy . --strict --show-error-codes; then
    return_code=1
  fi

  echo "Pylint..."
  if ! touch __init__.py; then
    return_code=1
  fi
  if ! pylint "$(pwd)"; then
    return_code=1
  fi

  exit ${return_code}
}


run() {
  python manage.py grpcserver
}


source .venv/bin/activate

if [[ "${command}" == "test" ]]; then
  echo "Execute tests..."
  test

elif [[ "${command}" == "run" ]]; then
  echo "Running development server..."
  run

else
  echo "Unsupported command ${command}!"
  exit 1
fi

