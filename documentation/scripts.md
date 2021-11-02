# Utility scripts

This project offers a bunch of utility scripts.
All of them expect to be run at the project root.

If the options `[GATE]` and `[SERVICE]` can be passed, either none or both have to be passed.
If none are passed, the script will iterate over *all* services, otherwise it will only be executed on the specified one.

## Operations

### `deploy.sh DEPLOYMENT`

This requires `kubectl` to be connected to a cluster.

1. Make sure that the namespace for the deployment exists

Note that in order for requests to reach the deployment, the appropriate entries will need to be manually added to `/etc/hosts`.

## Development

### `test.sh [GATE SERVICE]`

This will first build the test containers.
Afterwards, it will complete any tests configured - this includes:

* Unit and integration tests
* Linting
* Static type checking (for backgates and microservices)

### `create_new_service.sh`

This will create a new service.
It will prompt the user for some information:

1. The `gate` this new service is for
1. The `type` of service:
   * gate

Afterwards, it will do the following:

1. Add the new service to `scripts/gate_service` and `.github/data/services.json`

For gates, it will additionally create the following:

* A skeleton react project to hold the frontgate code

Of course, you should thoroughly review the `git` diff before committing anything to source control.

The `templates` folder contains the data necessary for this script to work and is documented [here](/documentation/templates.md).

## Helpers

These scripts are not intended to be called directly, but are used by the other scripts.

### `build.sh ENVIRONMENT [GATE SERVICE]`

This will build the containers for either the `development` or `production` environment.
If no service was specified, it will do so for *all* services.
Otherwise, it will only do so for the specified service.

Afterwards, any dangling images get pruned.

### `service_loop.sh FUNCTION [GATE SERVICE]`

If no service was specified, the function gets executed on *all* services.
If a service was specified, the function gets executed on the specified service.
