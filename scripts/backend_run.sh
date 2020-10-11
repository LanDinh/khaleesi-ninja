#!/bin/bash

err=0
trap 'err=1' ERR

# Perform the tests, linter, and static type checker.
coverage run "backend/${BACKEND_PROJECT}/manage.py" test
pylint --rcfile "backend/pylintrc" "backend/${BACKEND_PROJECT}/"

# Mypy needs special treatment...
cd backend/
sed -i -e "s/BACKEND_PROJECT/${BACKEND_PROJECT}/g" "mypy.ini"
mypy --strict --show-error-codes "${BACKEND_PROJECT}/"
cd ..

test $err = 0
