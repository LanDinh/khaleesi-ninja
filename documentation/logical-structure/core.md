# core

This app contains the common logic shared by all apps.

![Core Structure](/documentation/images/logical-structure/core.svg)

## frontend

## clocktower

## sawmill

This service is responsible for logging.

![Sawmill Structure](/documentation/images/logical-structure/core-sawmill.svg)

The different types of logs are:

* `Metadata` contains metadata shared by all log types
* `ResponseMetadata` contains metadata shared by all request log types
* `Error` contains information regarding errors that happened
* `Event` contains information relating to actions that might require auditing
* `Query` contains information regarding database queries
* `GrpcRequest` contains information regarding gRPC requests and their responses
* `HttpRequest` contains information regarding requests as they enter the ecosystem
