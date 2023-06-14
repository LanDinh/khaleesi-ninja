# CI via Github Actions

## Actions folder

### `cache-image`

Place a built image into the cache for reuse.

### `clean-cache`

Remove everything from the cache that was added within a specific build hash.

### `get-cached-backend-data`

Load backend base images located inside the cache.

### `load-all-images`

Load all images located inside the cache.

### `load-image`

Load a specific image located inside the cache.

### `set-json-output`

This will read the json files in the `data` folder and make them available as output.

## Workflows folder

### `clean-cache`

Clean up cache from an old run in case cleanup failed at the end of the run.

### `codeql-analysis`

Github-provided code quality tool.

### `delete-old-workflow-runs`

Make it possible to remove old workflow results after a workflow got renamed.

### `tests`

This workflow is executed for every push.
It contains the following jobs:

1. `matrix` will read data lists to make those available to other jobs for use in their strategy matrix.
1. `test-kubernetes-configuration` spins up the environments to verify that both the kubernetes configuration as well as `./scripts/operations/deploy.sh` are working.
1. `test-all-services` will call `./scripts/development/test.sh` per service to execute all tests for all services. 
