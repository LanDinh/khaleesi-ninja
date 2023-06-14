# Kubernetes Structure

## Logical Structure

![Kubernetes Logical Structure](/documentation/images/folder-structure/kubernetes-logical-structure.svg)

Each app has the same base structure within kubernetes.

It has a `frontend`, which serves the SPA to the user via an `ingress` configuration.
There are multiple `microservices` which have access to their own `postgres` databases deployed by `kubegres`.
`gRPC UI` can be used to debug these microservices.

One `prometheus` instance scrapes metrics from everywhere, and they are available via `grafana` dashboards.

### Conventions

| Port | Use             |
|------|-----------------|
| 8000 | General service |
| 8010 | Sidecar proxy   |
| 8020 | Metrics         |

## Folder Structure

All kubernetes configuration is managed via `helm` charts.

### `configuration`

The configuration consists of four parts, all of which must be specified when installing a helm chart:

* environment: this contains environment-specific configuration like e.g. the domain used for that environment
* app: this contains app-specific configuration, like e.g. the number of postgres replicas to use for the database
* type: this contains service-type specific configuration, like e.g. if an ingress resource should be set up
* service: this contains service-specific configuration, like e.g. how many replicas should be used for that service
* third-party: this contains configuration necessary for third parties
  * `kube-prometheus-stack.yml` is the configuration of the monitoring stack

The combination of these parts must provide valid input for the helm charts.
They are passed in order, with the exception of the environment, which is last.
That way, the more specific types can override the less specific configuration, with the environment bein able to override everything (e.g. in `development`, only a single replica is required per service).

### `khaleesi-ninja-cluster`

This contains basic resources that are shared cluster-wide:

* third-party grafana dashboards
  * nginx: [last update](https://github.com/nginxinc/nginx-prometheus-exporter/tree/master/grafana) on 2020-07-17

### `khaleesi-ninja-environment`

This contains basic resources necessary for the ecosystem to work:

* namespace
* ingress class
* default configuration to use for `grpc-web` `envoy` proxies
* default configuration to use for `kubegres` - this includes:
  * SQL script to install extensions, create users & databases
  * SQL script to apply user permissions
  
Additionally, the following resources are necessary for monitoring:

* `prometheus` instance, including
  * service account & role binding
  * service & service monitor
* `grafana` datasource for the `prometheus` instance, including custom dashboards
* `ingress` making monitoring accessible
    
### `khaleesi-ninja-app`

This contains basic resources shared within an app:

* `kubegres` manifest to deploy a database cluster
* `kubegres` instance configuration - this includes:
  * `kubegres` host
  * `kubegres` port
  * `kubegres` superuser name
* development credentials if required - this includes:
  * `kubegres` superuser password
  * `kubegres` replication user password
* `grafana` custom dashboards

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
