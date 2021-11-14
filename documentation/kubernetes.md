# Kubernetes Structure

## Logical Structure

![Kubernetes Folder Structure](/documentation/images/kubernetes-logical-structure.svg)

Each gate has the same base structure within kubernetes.

It has a frontgate, which serves the SPA to the user via an ingress configuration.
This SPA uses the backgate as entry point into the backend system.

The backgate, too, is available via an ingress configuration.
It calls its own micro services as well as the core micro services to serve content.

### Conventions

| Port | Use                     |
| ---- | ----------------------- |
| 8000 | General service         |

## Folder Structure

All kubernetes configuration is managed via `helm` charts.

### `khaleesi-ninja-infrastructure`

This contains basic infrastructure necessary for the ecosystem to work:

* namespace
* ingress class

It expects the following values:

* `environment` needs to be one of `development`, `integration`, `staging` and `production`

### `khaleesi-ninja-service`

This contains manifests necessary for the services to work:

* deployment
* service
* ingress (for frontgates and backgates)

It expects the following values:

* `environment` needs to be one of `development`, `integration`, `staging` and `production`
* `gate` needs to be one of `core`
* `service` needs to be the service name
* `version` needs to be the version to be installed for the environments `staging` and `production`
