# Kubernetes Structure

## Logical Structure

![Kubernetes Logical Structure](/documentation/images/kubernetes-logical-structure.svg)

Each gate has the same base structure within kubernetes.

It has a frontgate, which serves the SPA to the user via an ingress configuration.
This SPA uses the backgate as entry point into the backend system.

The backgate, too, is available via an ingress configuration.
It calls its own micro services as well as the core micro services to serve content.

### Conventions

| Port | Use                     |
| ---- | ----------------------- |
| 8000 | General service         |
| 8010 | Sidecar proxy           |

## Folder Structure

All kubernetes configuration is managed via `helm` charts.

### `configuration`

The configuration consists of four parts, all of which must be specified when installing a helm chart:

* environment: this contains environment-specific configuration like e.g. the domain used for that environment
* gate: this contains gate-specific configuration, like e.g. the number of postgres replicas to use for the database
* type: this contains service-type specific configuration, like e.g. if an ingress resource should be set up
* service: this contains service-specific configuration, like e.g. how many replicas should be used for that service

The combination of these parts must provide valid input for the helm charts.
They are passed in in reverse order, so that more generic configuration can override specific configuration (e.g. in `development`, only a single replica is required per service).

### `khaleesi-ninja-environment`

This contains basic resources necessary for the ecosystem to work:

* namespace
* ingress class
* default configuration to use for grpc-web envoy proxies

### `khaleesi-ninja-service`

This contains manifests necessary for the services to work:

* deployment
* service
* ingress (if required)

Furthermore, if grpcui is required, it will additionally deploy:
* grpcui deployment
* grpcui service
* grpcui ingress
