# Scripts

This project offers a bunch of scripts to ease operations & development.
All of them expect to be run at the project root.

If the options `[GATE]`, `[SERVICE]`, `[TYPE]`, `[VERSION]` and `[DEPLOY]` can be passed, either none or all have to be passed.
In some cases, a temporary file is used to pass this information, which is written to via an interactive prompt.
If no information is passed, the script will iterate over *all* services, otherwise it will only be executed on the specified one.

## `operations` folder

### `setup_cluster.sh`

This requires `kubectl` to be connected to a cluster.
Install all necessary controllers to the given cluster:

* `ingress-nginx`: the official `nginx` kubernetes controller, maintained by kubernetes
* `kubegres`: the `postgres` controller

### `setup_environment.sh ENVIRONMENT`

Install all necessary elements of the given environment:

* the `namespace` for the environment
* a `ingress-class` for use by the environment
* a `configmap` holding the default configuration for envoy used as grpc-web proxy

### `deploy.sh ENVIRONMENT [INTERACTIVE | (GATE SERVICE TYPE VERSION DEPLOY)]`

If no service was specified, this affects all services.
If `current_service` was specified, `./scripts/data/current_service` is used as input.
If this file doesn't exist, `./scripts/development/swich_current_service.sh` is called to create it.
If `GATE` and `SERVICE` were specified, the specified micro service is affected.

This applies the manifests for the given service.

If the `development` or `integration` environment was chosen, some more steps are executed:

1. The affected containers get rebuilt
1. The deployment gets a rolling restart

### `refresh_tls_certificate.sh`

This can be used to refresh the TLS certificate.
The contact email address has to be set as environment variable (`KHALEESI_EMAIL`), as well as the affected domain ('KHALEESI_DOMAIN').
It will be put into the folder `letsencrypt` - note that this folder is listed in `.gitignore` so as not to leak any private keys.

### `recreate_tls_certificate.sh`

This can be used to recreate the kubernetes secret holding the TLS certificate (e.g. if the namespace gets set up from scratch)

## `development` folder

### `test.sh [INTERACTIVE | (GATE SERVICE TYPE VERSION DEPLOY)]`

If no service was specified, this affects all services.
If `current_service` was specified, `./scripts/data/current_service` is used as input.
If this file doesn't exist, `./scripts/development/swich_current_service.sh` is called to create it.
If `GATE` and `SERVICE` were specified, the specified micro service is affected.

This will first build the test containers.
Afterwards, it will complete any tests configured - this includes:

* Unit and integration tests
* Linting
* Static type checking (for backgates and microservices)

### `generate_protos.sh`

This will generate the code for all proto files located in `/proto`.

### `switch_current_service.sh`

This will prompt the user to select the `current_service` that is used by `./development/test.sh` and `./operations/deploy.sh`.

### `make_migrations.sh`

This only exists in `current_service` mode.
It will prompt the user for the app name for which migrations should be created, and proceed with copying them into the correct migrations folder.

### `create_new_service.sh`

This will create a new service.
It will prompt the user for some information:

1. The `gate` this new service is for
1. The `type` of service:
   * gate

Afterwards, it will do the following:

1. Add the new service to `data/services.json`
1. Add kubernetes manifests for the service

For gates, it will additionally create the following:

* A skeleton `react` project to hold the frontgate code
* A skeleton `django` project to hold the backgate code

Of course, you should thoroughly review the `git` diff before committing anything to source control.

The `templates` folder contains the data necessary for this script to work and is documented [here](/documentation/templates.md).

## `util` folder

These scripts are not intended to be called directly, but are used by the other scripts.

### `build.sh MODE [GATE SERVICE]`

This will build the containers in either `development` or `production` mode.
If no service was specified, it will do so for *all* services.
Otherwise, it will only do so for the specified service.

Afterwards, any dangling images get pruned.

### `service_loop.sh FUNCTION [GATE SERVICE]`

If no service was specified, the function gets executed on *all* services.
If a service was specified, the function gets executed on the specified service.

### `parse_service.sh RAW_INPUT`

This will parse the raw input to extract service information from the json object.

### `valid_environment.sh ENVIRONMENT`

This validates that the provided environment exists.
