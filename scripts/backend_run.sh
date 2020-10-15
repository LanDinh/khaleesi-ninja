#!/bin/bash

err=0
trap 'err=1' ERR

cd "backend/${BACKEND_PROJECT}/"
PYTHONPATH=${PYTHONPATH}:$(pwd)
export PYTHONPATH
echo $PYTHONPATH
NO_SOURCE="__pycache__ .mypy_cache configuration"
DIRS=""

# Perform the tests.
coverage run "./manage.py" test
cp .coverage ../../.coverage.${BACKEND_PROJECT}

# Perform the linter.
pylint "${BACKEND_PROJECT}" --rcfile "../pylintrc"

# Perform the static type checker.
for dir in */
do
    dir=${dir%*/}  # remove the trailing "/"
    dir=${dir##*/}  # print everything after the final "/"
    if ! [[ " ${NO_SOURCE} " =~ .*\ ${dir}\ .* ]]
    then
      DIRS="${DIRS} ${dir}"
    fi
done
mypy --show-error-codes --strict --config-file "../mypy.ini" ${DIRS}

cd ..

test $err = 0
