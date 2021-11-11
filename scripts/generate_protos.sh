#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Options.
proto_in="proto"
python_in="proto/python"
python_out="backend/khaleesi/proto"


echo "Clean up old files and create mount directory..."
rm -r -f temp
mkdir temp

echo "Generating the python protos..."
rm -f "${python_out}/"*
mkdir -p "${python_out}"
cp "${python_in}/__init__.py" "${python_out}/__init__.py"
python -m pip install -r "${python_in}/requirements.txt"
python -m grpc_tools.protoc -I proto --python_out="${python_out}" --grpc_python_out="${python_out}" --mypy_out="${python_out}" "${proto_in}"/*.proto
