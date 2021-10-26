# khaleesi-ninja

![CI badge](https://github.com/LanDinh/khaleesi-ninja/actions/workflows/tests.yml/badge.svg?branch=main)
![lines of code badge](https://img.shields.io/tokei/lines/github/LanDinh/khaleesi-ninja)
![licence badge](https://img.shields.io/github/license/LanDinh/khaleesi-ninja)

## Available deployments

| Deployment | Intended Use      | Differences in Configuration |
| ---------- | ----------------- | ---------------------------- |
| `local`    | Local development | Debug mode is active, requires changes to `/etc/hosts` |

## Getting Started

### Prerequisites

You need to make sure that these conditions are met:

* Setup a local kubernetes cluster (instructions are in their [official documentation](https://kubernetes.io/docs/setup/))
* If your local kubernetes setup didn't ship with it, you'll also need to install `kubectl` to control that cluster
* Edit your `/etc/hosts` point all of the endpoints mentioned above for the `local` deployment to your localhost
* If you also want to test the changes on your Android phone without rooting it, you will need to set up a proxy on your development machine and follow the instructions [here](https://developer.chrome.com/docs/devtools/remote-debugging/local-server/).

You might want to make yourself familiar with the technologies used:

Deployment:

![kubernetes badge](https://img.shields.io/badge/kubernetes-v1.21-informational)
![docker badge](https://img.shields.io/badge/docker-v20.10-informational)

Backend:

![python badge](https://img.shields.io/badge/python-v3.10-informational)

### Structure

The folder structure is as follows:

* `.github` CI related configuration - [documentation](documentation/ci.md)
* `documentation` A bunch of markdown files to document everything
* `kubernetes` Kubernetes related configuration - [documentation](documentation/kubernetes.md)
* `scripts` Utility scripts - [documentation](documentation/scripts.md)
