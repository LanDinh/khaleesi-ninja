#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Options.
line=${1}


# Parse the input.
IFS="\"" read -r -a split <<< "${line}"
site="${split[3]}"
app="${split[7]}"
type="${split[11]}"
version="${split[15]}"
deploy="${split[19]}"

echo "${site}" "${app}" "${type}" "${version}" "${deploy}"
