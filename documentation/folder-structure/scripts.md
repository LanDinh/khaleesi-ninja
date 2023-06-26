# Scripts

This project offers a bunch of scripts to ease operations & development.
All of them expect to be run at the project root.

## main scripts

These are the main scripts containing re-usable logic.
They are typically not called directly.

### `build.sh MODE [APP SERVICE]`

This will build the containers in either `development` or `production` mode.
Afterwards, any dangling images get pruned.


### `deploy.sh ENVIRONMENT [APP SERVICE TYPE VERSION DEPLOY DROP_DATABASE]`

If `DROP_DATABASE` was specified, it will completely wipe the database and re-apply all migrations.

This applies the manifests for the given service - see the [kubernetes documentation](kubernetes.md) for details.

If the `development` or `integration` environment was chosen, some more steps are executed:

1. The affected containers get rebuilt
1. The deployment gets a rolling restart


### `generate_protos.sh`

This will generate the code for all proto files located in `/proto`.


### `test.sh [APP SERVICE TYPE VERSION DEPLOY]`

This will first build the test containers.
Afterwards, it will execute any tests configured - this includes:

* Unit and integration tests
* Linting
* Static type checking

Test a service.

## `operations` folder

These contain operational scripts which need to be run from time to time.

### `refresh_tls_certificate.sh`

This can be used to refresh the TLS certificate.
The contact email address has to be set as environment variable (`KHALEESI_EMAIL`), as well as the affected domain ('KHALEESI_DOMAIN').
It will be put into the folder `letsencrypt` - note that this folder is listed in `.gitignore` so as not to leak any private keys.

### `setup_cluster.sh`

This requires `kubectl` to be connected to a cluster.
Install all necessary controllers to the given cluster:

* `ingress-nginx`: the official `nginx` kubernetes controller, maintained by kubernetes
* `kubegres`: the `postgres` controller

### `setup_environment.sh ENVIRONMENT`

Install all necessary elements of the given environment as well as all apps - see the [kubernetes documentation](kubernetes.md) for details.

## `local` folder

These scripts are used for local deployment & development.

### `adjust_grafana_dashboards.sh`

Grafana dashboards export final `json`, whereas we need to replace some of these things by variables that can be consumed by `helm`.

This adjusts the dashboards to not need manual effort to fix the generated `json`.

### `create_new_service.sh`

This will create a new service.
It will prompt the user for some information:

1. The `app` this new service is for
1. The `service` name of the new service
1. The `type` of service:
   * frontend
   * micro

Afterwards, it will do the following:

1. Add the new service to `data/services.json`
1. Add the new gate to `data/gates.json`
1. Add kubernetes manifests for the service

For frontends, it will additionally create a `remix` project to hold the frontend code.

For microservices, it will additionally create a `django` project to hold the microservice code.

Of course, you should thoroughly review the `git` diff before committing anything to source control.

The `templates` folder contains the data necessary for this script to work and is documented [here](/documentation/folder-structure/templates.md).

### `deploy.sh ENVIRONMENT [current_service [drop_database] | (APP SERVICE TYPE VERSION DEPLOY)]`

If no service was specified, this affects all services.
If `current_service` was specified, `./scripts/data/current_service` is used as input.
If this file doesn't exist, `./scripts/development/swich_current_service.sh` is called to create it.
If `drop_database` was specified additionally, it will completely wipe the database and re-apply all migrations.

If `APP` and `SERVICE` were specified, the specified micro service is affected.

This applies the manifests for the given service - see the [kubernetes documentation](kubernetes.md) for details.

If the `development` or `integration` environment was chosen, some more steps are executed:

1. The affected containers get rebuilt
1. The deployment gets a rolling restart

### `make_migrations.sh [APP]`

This only exists in `current_service` mode.
It will make the migrations for either the current microservice or the khaleesi migrations for the microservice.

### `switch_current_service.sh`

This will prompt the user to select the `current_service` that is used by `./development/test.sh` and `./operations/deploy.sh`.

### `test.sh [current_service | (APP SERVICE TYPE VERSION DEPLOY)]`

If no service was specified, this affects all services.
If `current_service` was specified, `./scripts/data/current_service` is used as input.
If this file doesn't exist, `./scripts/development/swich_current_service.sh` is called to create it.
If `APP` and `SERVICE` were specified, the specified micro service is affected.

This will first build the test containers.
Afterwards, it will execute any tests configured - this includes:

* Unit and integration tests
* Linting
* Static type checking

## `ci` folder

The scripts in this folder are used by the CI.

### `deploy.sh ENVIRONMENT`

This affects all services.

This applies the manifests for the given service - see the [kubernetes documentation](kubernetes.md) for details.

If the `development` or `integration` environment was chosen, some more steps are executed:

1. The affected containers get rebuilt
1. The deployment gets a rolling restart

## `util` folder

These are utility scripts that are never called directly.

### `build-backend-base.sh`

Build the base backend images to speed up development.

### `parse_environment.sh RAW_INPUT`

This will parse the raw input to extract environment information from the json object.

### `parse_service.sh RAW_INPUT`

This will parse the raw input to extract service information from the json object.

### `recreate_tls_certificate.sh`

This can be used to recreate the kubernetes secret holding the TLS certificate (e.g. if the namespace gets set up from scratch)

### `service_loop.sh FUNCTION [APP SERVICE]`

If no service was specified, the function gets executed on *all* services.
If a service was specified, the function gets executed on the specified service.

### `valid_environment.sh ENVIRONMENT`

This validates that the provided environment exists.
