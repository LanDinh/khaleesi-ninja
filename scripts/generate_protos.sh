#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Colors.
magenta='\033[0;35m'
yellow='\033[0;33m'
green='\033[0;32m'
clear_color='\033[0m'


# Options.
image_name="khaleesi-ninja/proto"
python_out="backend/khaleesi/proto"


build_protos() {
  local language=${1}

  echo "Building the image..."
  docker build "proto" --target "${language}" -t "${image_name}/${language}"

  echo "Generating the protos..."
  docker run --rm --mount "type=bind,source=$(pwd)/temp,target=/data" "${image_name}/${language}"
}


echo "Clean up old files and create mount directory..."
rm -r -f temp
mkdir temp

echo "Generating the python protos..."
build_protos python

echo "Replacing the old python protos..."
rm -f "${python_out}"/*
mkdir -p "${python_out}"
cp -r temp/* "${python_out}/"
