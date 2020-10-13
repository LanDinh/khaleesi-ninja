#!/bin/bash

err=0
trap 'err=1' ERR

# Perform the tests.
coverage run "backend/${BACKEND_PROJECT}/manage.py" test

cd "backend/${BACKEND_PROJECT}/"
NO_SOURCE="__pycache__ .mypy_cache configuration"

# Perform the linter.
pylint "backend/${BACKEND_PROJECT}/" --rcfile "../pylintrc"

# Perform the static type checker.
sed -e "s/BACKEND_PROJECT/${BACKEND_PROJECT}/g" "../mypy.ini" > "mypy_temp.ini"
echo ${PWD}
for dir in */
do
    dir=${dir%*/}  # remove the trailing "/"
    dir=${dir##*/}  # print everything after the final "/"
    echo ${dir}
    if ! [[ " ${NO_SOURCE} " =~ .*\ ${dir}\ .* ]]
    then
      echo doing something
      mypy "${dir}/" --show-error-codes --strict --config-file "mypy_temp.ini"
    fi
done
rm "mypy_temp.ini"

cd ..

test $err = 0
