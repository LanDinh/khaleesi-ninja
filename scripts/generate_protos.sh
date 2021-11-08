#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Options.
input="proto/proto"
python_out="backend/khaleesi"


echo "Clean up old files and create mount directory..."
rm -r -f temp
mkdir temp

echo "Generating the python protos..."
rm -f "${python_out}/proto/"*
mkdir -p "${python_out}"
cp proto/python/__init__.py "${python_out}/proto/__init__.py"
python -m pip install grpcio-tools
python -m pip install mypy-protobuf
python -m grpc_tools.protoc -I proto --python_out="${python_out}" --grpc_python_out="${python_out}" --mypy_out="${python_out}" "${input}"/*.proto
