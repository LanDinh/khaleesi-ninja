# khaleesi-ninja

![latest version](https://img.shields.io/github/v/tag/LanDinh/khaleesi-ninja)
[![CI badge](https://github.com/LanDinh/khaleesi-ninja/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/LanDinh/khaleesi-ninja/actions)
[![codecov badge](https://codecov.io/gh/LanDinh/khaleesi-ninja/branch/main/graph/badge.svg?token=tQrhEsgApq)](https://codecov.io/gh/LanDinh/khaleesi-ninja)
![lines of code badge](https://img.shields.io/tokei/lines/github/LanDinh/khaleesi-ninja)
[![licence badge](https://img.shields.io/github/license/LanDinh/khaleesi-ninja)](LICENSE)

## Available Systems

The following environments are ready to use.

| Environment       | Intended Use       | Install Location | Debug Mode         | Users              |
| ----------------- | ------------------ | ---------------- | ------------------ | ------------------ |
| `development`     | development        | localhost        | :heavy_check_mark: | self only          |
| `integration`     | development        | localhost        | :x:                | self only          |
| `staging`         | quality assurance  | upstream         | :x:                | selected few users |
| `production`      | production         | upstream         | :x:                | real users         |

The following gates are ready to use.

| Gate   | Domain | `production` | `staging`    | Use                      |
| ------ | ------ | ------------ | ------------ | ------------------------ |
| `core` | -      | not deployed | not deployed | Code shared by all gates |

## Getting Started

### Prerequisites

You need to make sure that these conditions are met:

* Setup a local kubernetes cluster (instructions are in their [official documentation](https://kubernetes.io/docs/setup/))
* If your local kubernetes setup didn't ship with it, you'll also need to install `kubectl` to control that cluster
* Install `helm` (instructions are in their [official documentation](https://helm.sh/docs/intro/install/))
* If you want to test the changes on your Android phone without rooting it, you will need to set up a proxy on your development machine and follow the instructions [here](https://developer.chrome.com/docs/devtools/remote-debugging/local-server/).

### Technologies used

You might want to make yourself familiar with the technologies used.

The general deployment is done with:

![helm badge](https://img.shields.io/badge/helm-v3.8-informational)
![kubernetes badge](https://img.shields.io/badge/kubernetes-v1.25-informational)
![docker badge](https://img.shields.io/badge/docker-v20.10-informational)

Other infrastructure consists of:

![kube-prometheus badge](https://img.shields.io/badge/kube--prometheus-latest-informational)

| Service Type     | General | Infrastructure | Development |
| ---------------- | ------- | -------------- | ----------- |
| Frontgate        | ![typescript badge](https://img.shields.io/badge/typescript-v4.4-informational) <br /> ![react badge](https://img.shields.io/badge/react-v17.0-informational) <br /> ![react-router badge](https://img.shields.io/badge/react--router-v6.0-informational) <br /> ![grpc-web badge](https://img.shields.io/badge/grpc--web-v6.0-informational) | ![nginx badge](https://img.shields.io/badge/nginx-v1.21-informational) </br> ![nginx-prometheus-exporter badge](https://img.shields.io/badge/nginx--prometheus--exporter-v0.9-informational) | ![create-react-app badge](https://img.shields.io/badge/create--react--app-latest-informational) <br /> ![jest badge](https://img.shields.io/badge/jest-v26.0-informational) <br /> ![eslint badge](https://img.shields.io/badge/eslint-latest-informational) |
| Backgate / Micro | ![python badge](https://img.shields.io/badge/python-v3.10-informational) <br /> ![grpcio badge](https://img.shields.io/badge/grpcio-v1.47-informational) <br /> ![django badge](https://img.shields.io/badge/django-v4.0-informational) | ![kubegres badge](https://img.shields.io/badge/kubegres-v1.16-informational) | ![grpcui badge](https://img.shields.io/badge/grpcui-latest-informational) <br /> ![grpcio-tools badge](https://img.shields.io/badge/grpcio--tools-v1.47-informational) <br /> ![pylint badge](https://img.shields.io/badge/pylint-v2.14-informational) <br /> ![mypy badge](https://img.shields.io/badge/mypy-v0.961-informational) |
| Backgate         | | ![envoy badge](https://img.shields.io/badge/envoy-v1.20-informational) | |

### Structure

The folder structure is as follows:

* `backend` The code for the backgates and microservices. They are grouped by gate. One `django` project per service.
* `.github` CI related configuration - [documentation](documentation/folder-structure/ci.md)
* `data` Lists of things (e.g. services, environments etc.) in json formats
* `documentation` A bunch of markdown files to document everything
* `frontgate` The code for the frontgates. One `react` project per frontgate.
* `kubernetes` Kubernetes related configuration - [documentation](documentation/folder-structure/kubernetes.md)
* `proto` Protobuf definitions
* `scripts` Utility scripts - [documentation](documentation/folder-structure/scripts.md)
* `templates` Templates used when creating new services - [documentation](documentation/folder-structure/templates.md)

The logical structure is as follows: 

* Each `gate` covers a specific group of use cases, and they all contain the following elements:
  * A `frontgate` which serves a SPA to browsers.
    To create a new `frontgate`, use its [custom template](/templates/frontgate/cra-template-khaleesi-ninja-frontgate)
  * A `backgate` which serves as entry point into the backend system.
    The `frontgate` communicates with the `backgate` via `grpc-web`
    To create a new `backgate`, use its [custom template](/templates/backend/backgate_template)
  * Multiple microservices, which encapsulate different functions from each other.
    They communicate with each other and the `backgate` via `grpc`.
    To create a new microservice, use its [custom template](/templates/backend/micro_template)
* The different gates are:
  * `core`: bundle common logic - [documentation](/documentation/logical-structure/core.md)

### Starting the ecosystem locally

Build and deploy changes by running the following commands (for local deployments, the environment will be either `development` or `integration`):

1. `./scripts/operations/setup_cluster.sh` will add the necessary controllers to the cluster
1. `./scripts/operations/setup_environment.sh <ENVIRONMENT>` will set up resources for the chosen environment
1. `./scripts/operations/deploy.sh <ENVIRONMENT>` will start up all gates and services for that environment

If self-signed TLS certificates are required, make sure that the following files exist:

* Private key: `letsencrypt/live/live/<ENVIRONMENT>.khaleesi.ninja/privkey.pem`
* Certificate: `letsencrypt/live/live/<ENVIRONMENT>.khaleesi.ninja/fullchain.pem`

This happens ideally before step 2, otherwise, simply repeat step 2.

### Automated tests

Execute the tests by running `./scripts/development/test.sh`

### Hints

* For local development, it is typical to work on a single service for a lengthy amount of time.
  To make this more user friendly, it is possible to pass the argument `current_service` to both `./scripts/development/test.sh` as well as `./scripts/operations/deploy.sh` (in front of all optional arguments).
  The first time `current_service` is passed, an interactive prompt will require choosing the service to be worked on.
  When it is time to switch work to a different service, simply call `./scripts/development/switch_current_service.sh`.
  
### Upgrades

Infrastructure: test.yml, scripts, kubernetes/configuration
Backend: requirements.txt, requirements-development.txt, requirements-service.txt
Frontgate: package.json
