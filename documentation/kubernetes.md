# Kubernetes Structure

## Logical Structure

![Kubernetes Folder Structure](/documentation/images/kubernetes-logical-structure.svg)

Each gate has the same base structure within kubernetes.

It has a frontgate, which serves the SPA to the user via an ingress configuration.
This SPA uses the backgate as entry point into the backend system.

The backgate, too, is available via an ingress configuration.
It calls its own micro services as well the core micro services to serve content.

## Folder Structure

![Kubernetes Folder Structure](/documentation/images/kubernetes-folder-structure.svg)

### `base` folder

The `service` directory contains the bare minimum shared by all khaleesi services:

* `deployment.yml` defines the kubernetes deployment
* `service.yml` defines the kubernetes service
* `kustomization.yml` collects all resources

The `frontgate` directory additionally contains some manifests shared by all frontgates:

* `ingress.yml` defines the ingress configuration to access the frontgate from the outside

### `service` folder

The `service` directory contains the kustomization shared by all services:

* a unique name prefix comprising of the gate and service
* labels indicating the gate and service
* an annotation to indicate the type of service
* the name of the image to use for this service

The `frontgate` directory adds kustomization for all frontgates

* a patch to change the hostname to the correct gate

### `environment` folder

For each environment, the following kustomizations are added for frontgates:

* a patch to change the hostname to the correct environment-subdomain
