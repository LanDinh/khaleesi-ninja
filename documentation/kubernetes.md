# Kubernetes Structure

![Kubernetes Structure](/documentation/images/kubernetes.svg)

The `base` directory contains the basic necessary manifests for each deployment:

* `deployment.yml` defines the kubernetes deployment
* `kustomization.yml` collects all resources

Each service has a dedicated folder within the `service` directory to allow kustomization per-service.
The minimum kustomization shared by all services is:

* a unique `namePrefix` comprising of the gate and service
* labels indicating the gate and service
* an annotation to indicate the type of service
* the name of the image to use for this service

Each environment has its own folder within the `environment` folder.
Inside each environment, each service has yet another dedicated folder to allow per-environment kustomization.
The minimum kustomization shared by all environments is:

* the namespace belonging to that environment
