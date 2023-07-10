# Backend

The code shared by all backends is located at `backend/khaleesi`.
It is structured as follows:

* `core` contains shared code.
  * `batch` contains code for batch job execution.
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
* `management` contains a custom management command to start the server.
* `migrations` contains the database migrations.
* `models` contains the models shared by all services.
* `proto` contains the generated proto files.


# Frontend

The code shared by all frontends is located at `frontend/khaleesi`.
It is structured as follows:

* `components` contains shared components.
  * `navigation` contains the code for the navigation bar and breadcrumbs.
  * `document` contains the main HTML document.
  * `error` contains a styled error page.
  * `icon` contains shared icons.
* `proto` contains generated proto files.
* `styles` contains common CSS.
