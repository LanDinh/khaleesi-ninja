#!/bin/bash

set -e
set -o pipefail

# Upload the results to codecov.
npm install -g codecov
codecov