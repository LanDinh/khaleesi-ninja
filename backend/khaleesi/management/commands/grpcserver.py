"""Command to start the gRPC server."""

# Python.
from concurrent import futures
from signal import signal, SIGTERM
from typing import Any

# Django.
from django.core.management.base import BaseCommand, CommandParser
from django.conf import settings
from django.utils.module_loading import import_string

# gRPC.
import grpc
from grpc_reflection.v1alpha import reflection

# prometheus.
# noinspection PyProtectedMember
from prometheus_client import start_http_server  # type: ignore[import] # https://github.com/prometheus/client_python/issues/491 # pylint: disable=line-too-long

# khaleesi.ninja.
from khaleesi.core.grpc import add_request_metadata
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.metrics.health import HEALTH as HEALTH_METRIC, HealthMetricType
from khaleesi.core.settings.definition import KhaleesiNinjaSettings, StructuredLoggingMethod
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
from khaleesi.proto.core_sawmill_pb2_grpc import LumberjackStub


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


class Command(BaseCommand):
  """Command to start the gRPC server."""
  help = 'Starts the gRPC server.'

  def add_arguments(self, parser: CommandParser) -> None :
    parser.add_argument(
      'address', nargs = '?', default = f'[::]:{khaleesi_settings["GRPC"]["PORT"]}',
      help = 'Optional address for which to open a port.'
    )
    parser.add_argument(
      '--max-workers', type = int, default = 10, dest = 'max_workers',
      help = 'Number of maximum worker threads.'
    )

  def handle(self, *args: Any, **options: Any) -> None :
    self.run(**options)

  def run(self, **options: Any) -> None :
    """Run the server."""
    self._serve(**options)

  def _serve(self, **options: Any) -> None :
    """Start the server."""

    def handle_sigterm(*_: Any) -> None :
      """Shutdown gracefully."""
      try:
        self.stdout.write(f'Stopping gRPC server at {options["address"]}...')
        HEALTH_METRIC.set(value = HealthMetricType.TERMINATING)
        done_event = server.stop(30)
        self.stdout.write('Stop complete.')
        self._log_server_state_event(
          action = Event.Action.ActionType.END,
          result = Event.Action.ResultType.SUCCESS,
          details = 'Server stopped successfully.'
        )
        if not done_event.wait(30):
          self._log_server_state_event(
            action = Event.Action.ActionType.END,
            result = Event.Action.ResultType.ERROR,
            details = f'Server stop failed... time out instead of gracefully shutting down.',
          )
      except Exception as stop_exception:
        self._log_server_state_event(
          action = Event.Action.ActionType.END,
          result = Event.Action.ResultType.ERROR,
          details = f'Server stop failed... {type(stop_exception).__name__}: {str(stop_exception)}'
        )
        raise stop_exception from None

    try:
      interceptors = [ PrometheusServerInterceptor() ]
      server = grpc.server(
          futures.ThreadPoolExecutor(max_workers = options['max_workers']),
          interceptors = interceptors  # type: ignore[arg-type] # fixed upstream
      )
      self._add_handlers(server)
      server.add_insecure_port(options['address'])
      self.stdout.write(f'Starting gRPC server at {options["address"]}...')
      server.start()
      start_http_server(int(khaleesi_settings['MONITORING']['PORT']))
      signal(SIGTERM, handle_sigterm)
      self._log_server_state_event(
        action = Event.Action.ActionType.START,
        result = Event.Action.ResultType.SUCCESS,
        details = 'Server started successfully.'
      )
      server.wait_for_termination()
    except Exception as start_exception:
      self._log_server_state_event(
        action = Event.Action.ActionType.START,
        result = Event.Action.ResultType.ERROR,
        details = f'Server startup failed. {type(start_exception).__name__}: {str(start_exception)}'
      )
      raise start_exception from None


  @staticmethod
  def _add_handlers(server: grpc.Server) -> None :
    """
    Attempt to import a class from a string representation.
    """
    raw_handlers = khaleesi_settings['GRPC']['HANDLERS']
    service_names = [reflection.SERVICE_NAME]
    for raw_handler in raw_handlers:
      handler = f'{raw_handler}.service_configuration'
      try:
        service_configuration = import_string(handler)
        service_configuration.register_service(server)
        service_names.append(service_configuration.name)
      except ImportError as error:
        raise ImportError(f'Could not import "{handler}" for gRPC handler.') from error
    reflection.enable_server_reflection(service_names, server)

  @staticmethod
  def _server_state_event(
      *,
      action: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
      details: str,
  ) -> Event :
    """Create the event for logging the server state."""
    event = Event()
    # Metadata.
    add_request_metadata(
      request      = event,
      request_id   = '',  # Not initiated by a gRPC call.
      grpc_service = 'grpc-server',
      grpc_method  = Event.Action.ActionType.Name(action).lower(),
      user_id      = 'grpc-server',
      user_type    = User.UserType.SYSTEM,
    )
    # Event target.
    event.target.type = 'core.core.server'
    # Event action.
    event.action.crud_type = action
    event.action.result    = result
    event.action.details   = details

    return event

  def _log_server_state_event(
      self, *,
      action: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log the server state."""
    event = self._server_state_event(action = action, result = result, details = details)
    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      channel = grpc.insecure_channel(f'core-sawmill:{khaleesi_settings["GRPC"]["PORT"]}')
      stub = LumberjackStub(channel)  # type: ignore[no-untyped-call]
      stub.LogEvent(event)
    else:
      # Send directly to the DB. Note that Events must be present in the schema!
      from microservice.models import Event as DbEvent  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      DbEvent.objects.log_event(grpc_event = event)
