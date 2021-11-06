# khaleesi-ninja

![latest version](https://img.shields.io/github/v/tag/LanDinh/khaleesi-ninja)
![CI badge](https://github.com/LanDinh/khaleesi-ninja/actions/workflows/tests.yml/badge.svg?branch=main)
[![codecov badge](https://codecov.io/gh/LanDinh/khaleesi-ninja/branch/main/graph/badge.svg?token=tQrhEsgApq)](https://codecov.io/gh/LanDinh/khaleesi-ninja)
![lines of code badge](https://img.shields.io/tokei/lines/github/LanDinh/khaleesi-ninja)
![licence badge](https://img.shields.io/github/license/LanDinh/khaleesi-ninja)

## Available Systems

| Environment       | Intended Use | Differences in Configuration |
| ----------------- | ------------ | ---------------------------- |
| `development`     | development  | Debug mode is active         |

Note that when deploying an environment locally, it is necessary to edit `/etc/hosts` to make it reachable.

| Gate   | Domain | Use |
| ------ | ------ | --- |
| `core` | - | Code shared by all gates |

## Getting Started

### Prerequisites

You need to make sure that these conditions are met:

* Setup a local kubernetes cluster (instructions are in their [official documentation](https://kubernetes.io/docs/setup/))
* If your local kubernetes setup didn't ship with it, you'll also need to install `kubectl` to control that cluster
* Edit your `/etc/hosts` point all of the endpoints mentioned above for the `local` environment to your localhost
* If you also want to test the changes on your Android phone without rooting it, you will need to set up a proxy on your development machine and follow the instructions [here](https://developer.chrome.com/docs/devtools/remote-debugging/local-server/).

### Technologies used

You might want to make yourself familiar with the technologies used:

Deployment:

![kubernetes badge](https://img.shields.io/badge/kubernetes-v1.21-informational)
![docker badge](https://img.shields.io/badge/docker-v20.10-informational)

Backgates:

![python badge](https://img.shields.io/badge/python-v3.10-informational)

Frontgates:

![typescript badge](https://img.shields.io/badge/typescript-v4.4-informational)
![react badge](https://img.shields.io/badge/react-v17.0-informational)
![create-react-app badge](https://img.shields.io/badge/create_react_app-latest-informational)
![jest badge](https://img.shields.io/badge/jest-v26.0-informational)
![eslint badge](https://img.shields.io/badge/eslint-latest-informational)

### Structure

The folder structure is as follows:

* `.github` CI related configuration - [documentation](documentation/ci.md)
* `documentation` A bunch of markdown files to document everything
* `frontgate` The code for the frontgates. One `react` project per frontgate - [documentation](documentation/frontgate.md)
* `kubernetes` Kubernetes related configuration - [documentation](documentation/kubernetes.md)
* `scripts` Utility scripts - [documentation](documentation/scripts.md)
* `templates` Templates used when creating new services - [documentation](documentation/templates.md)

### Starting the gates locally in development mode

Build and deploy changes by running `./scripts/deploy.sh development`

### Automated tests

Execute the tests by running `./scripts/test.sh`
