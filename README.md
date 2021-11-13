# khaleesi-ninja

![latest version](https://img.shields.io/github/v/tag/LanDinh/khaleesi-ninja)
![CI badge](https://github.com/LanDinh/khaleesi-ninja/actions/workflows/tests.yml/badge.svg?branch=main)
[![codecov badge](https://codecov.io/gh/LanDinh/khaleesi-ninja/branch/main/graph/badge.svg?token=tQrhEsgApq)](https://codecov.io/gh/LanDinh/khaleesi-ninja)
![lines of code badge](https://img.shields.io/tokei/lines/github/LanDinh/khaleesi-ninja)
![licence badge](https://img.shields.io/github/license/LanDinh/khaleesi-ninja)

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

![helm badge](https://img.shields.io/badge/helm-v3.7-informational)
![kubernetes badge](https://img.shields.io/badge/kubernetes-v1.22-informational)
![docker badge](https://img.shields.io/badge/docker-v20.10-informational)

| Service Type | General | Deployment | Development |
| ------------ | ------- | ---------- | ----------- |
| Frontgate    | ![typescript badge](https://img.shields.io/badge/typescript-v4.4-informational) <br /> ![react badge](https://img.shields.io/badge/react-v17.0-informational) <br /> ![react-router badge](https://img.shields.io/badge/react_router-v6.0-informational) | ![nginx badge](https://img.shields.io/badge/nginx-v1.21-informational) | ![create-react-app badge](https://img.shields.io/badge/create_react_app-latest-informational) <br /> ![jest badge](https://img.shields.io/badge/jest-v26.0-informational) <br /> ![eslint badge](https://img.shields.io/badge/eslint-latest-informational) |
| Backgate     | ![python badge](https://img.shields.io/badge/python-v3.10-informational) <br /> ![grpcio badge](https://img.shields.io/badge/grpcio-v1.14-informational) <br /> ![django badge](https://img.shields.io/badge/django-v3.2-informational) | | ![grpcio_tools badge](https://img.shields.io/badge/grpcio_tools-v1.41-informational) <br /> ![mypy-protobuf badge](https://img.shields.io/badge/mypy_protobuf-v3.0-informational)

### Structure

The folder structure is as follows:

* `.github` CI related configuration - [documentation](documentation/ci.md)
* `documentation` A bunch of markdown files to document everything
* `frontgate` The code for the frontgates. One `react` project per frontgate - [documentation](documentation/frontgate.md)
* `kubernetes` Kubernetes related configuration - [documentation](documentation/kubernetes.md)
* `proto` Protobuf definitions
* `scripts` Utility scripts - [documentation](documentation/scripts.md)
* `templates` Templates used when creating new services - [documentation](documentation/templates.md)

### Starting the ecosystem locally

Build and deploy changes by running the following command (for local deployments, the environment will be either `development` or `integration`):

```
./scripts/operations/deploy.sh <ENVIRONMENT>
```

Optionally, self-signed TLS certificates may be made available to deployments using the following command:

```
  .scripts/operations/recreate_tls_certificate.sh
```

Note that this expects the following files to exist:

* Private key: `letsencrypt/live/live/<ENVIRONMENT>.khaleesi.ninja/privkey.pem`
* Certificate: `letsencrypt/live/live/<ENVIRONMENT>.khaleesi.ninja/fullchain.pem`

### Automated tests

Execute the tests by running `./scripts/development/test.sh`

### Hints

* For local development, it is typical to work on a single service for a lengthy amount of time.
  To make this more user friendly, it is possible to pass the argument `current_service` to both `./scripts/development/test.sh` as well as `./scripts/operations/deploy.sh` (in front of all optional arguments).
  The first time `current_service` is passed, an interactive prompt will require choosing the service to be worked on.
  When it is time to switch work to a different service, simply call `./scripts/development/switch_current_service.sh`.
