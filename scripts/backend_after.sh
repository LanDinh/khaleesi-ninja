#!/bin/bash

set -e
set -o pipefail

# Upload the results to codecov.
pip install codecov
codecov