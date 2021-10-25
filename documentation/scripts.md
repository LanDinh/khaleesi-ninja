# Utility scripts

This project offers a bunch of utility scripts.
All of them expect to be run at the project root.

## Operations

### `deploy.sh DEPLOYMENT`

This requires `kubectl` to be connected to a cluster.

1. Make sure that the namespace for the deployment exists

Note that in order for requests to reach the deployment, the appropriate entries will need to be manually added to `/etc/hosts`.
