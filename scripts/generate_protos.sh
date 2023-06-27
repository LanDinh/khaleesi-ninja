#!/bin/bash

# set -x          # Print subcommands to terminal.
set -e          # Fail if any command fails
set -u          # Define variables before usage
set -o pipefail # Make pipes fail


# Options.
proto_in="proto"
python_in="backend/requirements-proto.txt"
python_out="backend/khaleesi/proto"
typescript_out="frontend/khaleesi/app/khaleesi/proto"


echo "Generating the python protos..."
rm -f "${python_out}/"*
mkdir -p "${python_out}"
touch "${python_out}/__init__.py"
python -m pip install -r "${python_in}"
python -m grpc_tools.protoc -I "${proto_in}" --python_out="${python_out}" --grpc_python_out="${python_out}" --mypy_out="${python_out}" "${proto_in}"/*.proto

echo "Generating the typescript protos..."
rm -f "${typescript_out}/"*
mkdir -p "${typescript_out}"
protoc -I="${proto_in}" --js_out=import_style=commonjs:"${typescript_out}" --grpc-web_out=import_style=commonjs+dts,mode=grpcweb:"${typescript_out}" "${proto_in}"/*.proto
