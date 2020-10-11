#!/bin/bash

err=0
trap 'err=1' ERR

# Perform the tests and linter
npm --prefix frontend run coverage
npm --prefix frontend run lint
npm --prefix frontend run build

test $err = 0
