# Scripts

This project offers a bunch of scripts to ease operations & development.
All of them expect to be run at the project root.

If the options `[GATE]` and `[SERVICE]` can be passed, either none or both have to be passed.
In some cases, a temporary file is used to pass this information, which is written to via an interactive prompt.
If no information is passed, the script will iterate over *all* services, otherwise it will only be executed on the specified one.

## `data` folder

* `environments` lists all available environments
* `gate_services` lists all available services
* `current_service` is an optional file for development to enable quick iterations of testing and deploying. It is not committed to `git`

## `operations` folder

### `setup_cluster.sh`

This requires `kubectl` to be connected to a cluster.
Install all necessary controllers to the given cluster:

* `ingress-nginx`: the official `nginx` kubernetes controller, maintained by kubernetes

### `setup_environment.sh`

Install all necessary elements of the given environment:

* `namespace`
* `ingress-class`

### `deploy.sh ENVIRONMENT [INTERACTIVE | (GATE SERVICE)]`

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

### `test.sh [INTERACTIVE | (GATE SERVICE)]`

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

### `create_new_service.sh`

This will create a new service.
It will prompt the user for some information:

1. The `gate` this new service is for
1. The `type` of service:
   * gate

Afterwards, it will do the following:

1. Add the new service to `scripts/gate_service` and `.github/data/services.json`

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

### `valid_environment.sh ENVIRONMENT`

This validates that the provided environment exists.

### `valid_service.sh GATE SERVICE`

This validates that the provided service exists.
