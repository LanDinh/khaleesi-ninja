#!/bin/bash

set -e
set -o pipefail

# Upload the results to codecov.
coverage combine
pip install codecov
codecov