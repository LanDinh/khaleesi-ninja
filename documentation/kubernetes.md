# Kubernetes Structure

## Logical Structure

![Kubernetes Logical Structure](/documentation/images/kubernetes-logical-structure.svg)

Each gate has the same base structure within kubernetes.

It has a `frontgate`, which serves the SPA to the user via an `ingress` configuration and inherits from the `core frontgate`.
This SPA uses the backgate as entry point into the backend system.

The `backgate`, too, is available via an `ingress` configuration, and inherits from the `core backgate`.
It calls its own `microservices` as well as the `core microservices` to serve content.

Both the `backgates` and `microservices` have access to the `postgres` database deployed by `kubegres`.
They also expose their API via `gRPC UI`.

### Conventions

| Port | Use                     |
| ---- | ----------------------- |
| 8000 | General service         |
| 8010 | Sidecar proxy           |
| 8020 | Metrics                 |

## Folder Structure

All kubernetes configuration is managed via `helm` charts.

### `configuration`

The configuration consists of four parts, all of which must be specified when installing a helm chart:

* environment: this contains environment-specific configuration like e.g. the domain used for that environment
* gate: this contains gate-specific configuration, like e.g. the number of postgres replicas to use for the database
* type: this contains service-type specific configuration, like e.g. if an ingress resource should be set up
* service: this contains service-specific configuration, like e.g. how many replicas should be used for that service
* third-party: this contains configuration necessary for third parties
  * `kube-prometheus-stack.yml` is the configuration of the monitoring stack
  * grafana-dashboards contains third party dashboards
    * nginx: [last update](https://github.com/nginxinc/nginx-prometheus-exporter/tree/master/grafana) on 2020-07-17 

The combination of these parts must provide valid input for the helm charts.
They are passed in in reverse order, so that more generic configuration can override specific configuration (e.g. in `development`, only a single replica is required per service).

### `khaleesi-ninja-cluster`

This contains basic resources that are shared cluster-wide:

* third-party grafana dashboards

### `khaleesi-ninja-environment`

This contains basic resources necessary for the ecosystem to work:

* namespace
* ingress class
* default configuration to use for `grpc-web` `envoy` proxies
* default configuration to use for `kubegres` - this includes:
  * SQL script to install extensions, create users & databases
  * SQL script to apply user permissions
  
Additionally, the following resources are necessary for monitoring:

* prometheus instance
* service account & role binding for prometheus
* service & service monitor for prometheus
* grafana datasource for the prometheus instance
* grafana custom dashboards
    
### `khaleesi-ninja-gate`

This contains basic resources shared within a gate:

* `kubegres` manifest to deploy a database cluster
* `kubegres` instance configuration - this includes:
  * `kubegres` host
  * `kubegres` port
  * `kubegres` superuser name
* development credentials if required - this includes:
  * `kubegres` superuser password
  * `kubegres` replication user password

### `khaleesi-ninja-service`

This contains manifests necessary for the services to work:

* deployment
* service
* ingress (if required)
* service monitor for monitoring
* development credentials if required - this includes:
  * `django` secret key

If `kubegres` is required, it will additionally deploy:

* `kubegres` initialization job which will trigger user & database creation
* `kubegres` configuration - this includes:
  * `kubegres` database name
  * `kubegres` write user name
  * `kubegres` read user name
* development credentials if required - this includes:
  * `kubegres` write user password
  * `kubegres` read user password

If `grpcui` is required, it will additionally deploy:

* `grpcui` deployment
* `grpcui` service
* `grpcui` ingress
