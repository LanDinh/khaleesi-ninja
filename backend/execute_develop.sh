#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


command=${1}
arguments=${2:-}
parallel=


if [[ "${CI:-false}" == "true" ]]; then
  parallel=" --parallel"
fi


test() {
  arguments=${1:-}
  return_code=0

  echo "Django tests..."
  # shellcheck disable=SC2086
  if ! python -m coverage run manage.py test ${arguments} --settings=khaleesi.core.settings.unittest"${parallel}"; then
    return_code=1
  fi

  echo "Copy coverage reports..."
  if ! mkdir -p /data/coverage; then
    return_code=1
  fi
  if ! python -m coverage xml; then
    return_code=1
  fi
  if ! cp -a coverage.xml "/data/coverage.xml"; then
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
  # exec is necessary to properly handle SIGTERM
  exec python -u manage.py grpcserver --settings khaleesi.core.settings.production
}

make_migrations() {
  app=${1}
  python manage.py makemigrations "${app}" --settings khaleesi.core.settings.unittest
  cp -a "${app}/migrations"/* /data/
}


source ../../.venv/bin/activate

if [[ "${command}" == "test" ]]; then
  echo "Execute tests..."
  test "${arguments}"

elif [[ "${command}" == "run" ]]; then
  echo "Running development server..."
  run

elif [[ "${command}" == "make_migrations" ]]; then
  echo "Making migrations..."
  make_migrations "${2}"

else
  echo "Unsupported command ${command}!"
  exit 1
fi

