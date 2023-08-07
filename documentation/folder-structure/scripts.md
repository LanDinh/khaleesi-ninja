# Scripts

This project offers a bunch of scripts to ease operations & development.
All of them expect to be run at the project root.

## main scripts

These are the main scripts containing re-usable logic.
They are typically not called directly.

### `build.sh MODE [SITE APP]`

This will build the containers in either `development` or `production` mode.
Afterwards, any dangling images get pruned.


### `deploy.sh ENVIRONMENT [SITE APP TYPE VERSION DEPLOY DROP_DATABASE]`

If `DROP_DATABASE` was specified, it will completely wipe the database and re-apply all migrations.

This applies the manifests for the given app - see the [kubernetes documentation](kubernetes.md) for details.

If the `development` or `integration` environment was chosen, some more steps are executed:

1. The affected containers get rebuilt
1. The deployment gets a rolling restart


### `generate_protos.sh`

This will generate the code for all proto files located in `/proto`.


### `test.sh [SITE APP TYPE VERSION DEPLOY]`

This will first build the test containers.
Afterwards, it will execute any tests configured - this includes:

* Unit and integration tests
* Linting
* Static type checking

Test a app.

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

Install all necessary elements of the given environment as well as all sites - see the [kubernetes documentation](kubernetes.md) for details.

## `local` folder

These scripts are used for local deployment & development.

### `adjust_grafana_dashboards.sh`

Grafana dashboards export final `json`, whereas we need to replace some of these things by variables that can be consumed by `helm`.

This adjusts the dashboards to not need manual effort to fix the generated `json`.

### `create_new_app.sh`

This will create a new app.
It will prompt the user for some information:

1. The `site` this new app is for
1. The `app` name of the new app
1. The `type` of app:
   * frontend
   * micro

Afterwards, it will do the following:

1. Add the new app to `data/apps.json`
1. Add kubernetes manifests for the app

For frontends, it will additionally create a `remix` project to hold the frontend code.

For microservices, it will additionally create a `django` project to hold the microservice code.

Of course, you should thoroughly review the `git` diff before committing anything to source control.

The `templates` folder contains the data necessary for this script to work and is documented [here](/documentation/folder-structure/templates.md).

### `deploy.sh ENVIRONMENT [current_app [drop_database] | (SITE APP TYPE VERSION DEPLOY)]`

If no app was specified, this affects all apps.
If `current_app` was specified, `./scripts/data/current_app` is used as input.
If this file doesn't exist, `./scripts/development/swich_current_app.sh` is called to create it.
If `drop_database` was specified additionally, it will completely wipe the database and re-apply all migrations.

If `SITE` and `APP` were specified, the specified microservice is affected.

This applies the manifests for the given app - see the [kubernetes documentation](kubernetes.md) for details.

If the `development` or `integration` environment was chosen, some more steps are executed:

1. The affected containers get rebuilt
1. The deployment gets a rolling restart

### `make_migrations.sh [APP]`

This only exists in `current_app` mode.
It will make the migrations for either the current microservice or the khaleesi migrations for the microservice.

### `switch_current_app.sh`

This will prompt the user to select the `current_app` that is used by `./development/test.sh` and `./operations/deploy.sh`.

### `test.sh [current_app | (SITE APP TYPE VERSION DEPLOY)]`

If no app was specified, this affects all apps.
If `current_app` was specified, `./scripts/data/current_app` is used as input.
If this file doesn't exist, `./scripts/development/swich_current_app.sh` is called to create it.
If `SITE` and `APP` were specified, the specified microservice is affected.

This will first build the test containers.
Afterwards, it will execute any tests configured - this includes:

* Unit and integration tests
* Linting
* Static type checking

## `ci` folder

The scripts in this folder are used by the CI.

### `deploy.sh ENVIRONMENT`

This affects all apps.

This applies the manifests for the given app - see the [kubernetes documentation](kubernetes.md) for details.

If the `development` or `integration` environment was chosen, some more steps are executed:

1. The affected containers get rebuilt
1. The deployment gets a rolling restart

## `util` folder

These are utility scripts that are never called directly.

### `build-backend-base.sh`

Build the base backend images to speed up development.

### `parse_environment.sh RAW_INPUT`

This will parse the raw input to extract environment information from the json object.

### `parse_app.sh RAW_INPUT`

This will parse the raw input to extract app information from the json object.

### `recreate_tls_certificate.sh`

This can be used to recreate the kubernetes secret holding the TLS certificate (e.g. if the namespace gets set up from scratch)

### `app_loop.sh FUNCTION [SITE APP]`

If no app was specified, the function gets executed on *all* apps.
If a app was specified, the function gets executed on the specified app.

### `valid_environment.sh ENVIRONMENT`

This validates that the provided environment exists.
