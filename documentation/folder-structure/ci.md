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
1. `test-helm-cluster` will verify the helm template for the cluster.
1. `update-pip-cache` will ensure that the shared pip caches are available.
1. `generate-protos` will generate the protobuf code.
1. `build-backend-base-images` will build the backend base images which speeds up the build.
1. `build` will build all images.
1. `test-helm-environment` will verify the helm template for the environments.
1. `test-helm-gate` will verify the helm template for the gates.
1. `test-helm-service` will verify the helm template for the services.
1. `unit-test` will execute the unit tests of all services.
1. `e2e-tests` will spin up all deployments and execute the E2E tests on them.
1. `clean-cache` ensures that the cache is always as empty as possible.
