# Backend

The code shared by all backends is located at `backend/khaleesi`.
It is structured as follows:

* `core` contains shared code.
* `management` contains a custom management command to start the server.
* `migrations` contains the database migrations.
* `models` contains the models shared by all services.
* `proto` contains the generated proto files.

The shared code contains:

* `batch` contains code for batch job execution.
* `database_router` contains logic determining which database connection to use in a given query.
* `grpc` defines the gRPC server, including startup and graceful turn-down.
* `interceptors` contains both client and server interceptors:
  * logging
  * metric definition
  * request error handling 
* `logging` contains loggers for structured logging, text logging, and DB query logging.
* `metrics` defines the common metrics for health, requests, and audit events.
* `service` contains common gRPC services, e.g. for stopping running batch jobs.
* `settings` contains common settings.
* `shared` contains common code, e.g. state, exceptions, ...
* `test_util` contains test utility.

# Frontend

The code shared by all frontends is located at `frontend/khaleesi`.
It is structured as follows:

* `components` contains shared components.
* `proto` contains generated proto files.
* `styles` contains common CSS.

The shared components are as follows:

* `navigation` contains the code for the navigation bar. 
* `document` contains the main HTML document.
* `error` contains a styled error page.
* `icon` contains shared icons.
