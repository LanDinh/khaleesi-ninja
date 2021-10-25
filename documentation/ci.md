# CI via Github Actions

## Data folder

This folder contains some `json` files so that multiple jobs can share matrix configuration.

## Actions folder

### `set-json-output`

This will read the json files in the `data` folder and make them available as output.

## Workflows folder

### `tests`

This workflow is executed for every push.
It contains the following jobs:

1. `matrix` will read data lists to make those available to other jobs for use in their strategy matrix.
1. `test-kubernetes-configuration` spins up the deployments to verify that both the kubernetes configuration as well as `scripts/deploy.sh` are working.
