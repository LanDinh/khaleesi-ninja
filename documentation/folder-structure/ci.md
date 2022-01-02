# CI via Github Actions

## Actions folder

### `set-json-output`

This will read the json files in the `data` folder and make them available as output.

### `setup-protoc`

This will install protoc & plugins necessary for it

## Workflows folder

### `tests`

This workflow is executed for every push.
It contains the following jobs:

1. `matrix` will read data lists to make those available to other jobs for use in their strategy matrix.
1. `test-kubernetes-configuration` spins up the environments to verify that both the kubernetes configuration as well as `./scripts/operations/deploy.sh` are working.
1. `test-all-services` will call `./scripts/development/test.sh` per service to execute all tests for all services. 
