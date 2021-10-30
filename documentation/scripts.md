# Utility scripts

This project offers a bunch of utility scripts.
All of them expect to be run at the project root.

## `deploy.sh DEPLOYMENT`

This requires `kubectl` to be connected to a cluster.

1. Make sure that the namespace for the deployment exists

Note that in order for requests to reach the deployment, the appropriate entries will need to be manually added to `/etc/hosts`.

## `create_new_service.sh`

This will create a new service.
It will prompt the user for some information:

1. The `gate` this new service is for
1. The `type` of service:
   * gate

Afterwards, it will create the following:

For gates, it will additionally create the following:

* A skeleton react project to hold the frontgate code
