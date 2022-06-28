"""The gRPC server."""

# Python.
from concurrent.futures import ThreadPoolExecutor
from signal import signal, SIGTERM
from typing import Any

# Django.
from django.conf import settings
from django.utils.module_loading import import_string

# gRPC.
from grpc import server, Server as GrpcServer
from grpc_reflection.v1alpha import reflection

# khaleesi.ninja.
from khaleesi.core.grpc.channels import ChannelManager
from khaleesi.core.grpc.request_metadata import add_request_metadata
from khaleesi.core.interceptors.server.logging import LoggingServerInterceptor
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.metrics.health import HEALTH as HEALTH_METRIC, HealthMetricType
from khaleesi.core.settings.definition import KhaleesiNinjaSettings, StructuredLoggingMethod
from khaleesi.core.shared.logger import LOGGER
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
from khaleesi.proto.core_sawmill_pb2_grpc import LumberjackStub


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


class Server:
  """The gRPC server."""

  server: GrpcServer
  channel_manager: ChannelManager

  def __init__(self) -> None :
    try:
      self.channel_manager = ChannelManager()
      interceptors = [
          PrometheusServerInterceptor(),
          LoggingServerInterceptor(channel_manager = self.channel_manager),
      ]
      self.server = server(
        ThreadPoolExecutor(khaleesi_settings['GRPC']['THREADS']),
        interceptors = interceptors,  # type: ignore[arg-type]  # fixed upstream!
      )
      self.server.add_insecure_port(f'[::]:{khaleesi_settings["GRPC"]["PORT"]}')
      self._add_handlers()
      signal(SIGTERM, self._handle_sigterm)
      self._log_server_state_event(
        action = Event.Action.ActionType.START,
        result = Event.Action.ResultType.SUCCESS,
        details = 'Server started successfully.'
      )
    except Exception as exception:
      self._log_server_state_event(
        action = Event.Action.ActionType.START,
        result = Event.Action.ResultType.FATAL,
        details = f'Server start failed. {type(exception).__name__}: {str(exception)}'
      )
      raise exception from None

  def start(self) -> None :
    """Start the server."""
    self.server.start()
    self.server.wait_for_termination()

  def _add_handlers(self) -> None :
    """Attempt to import a class from a string representation."""
    raw_handlers = khaleesi_settings['GRPC']['HANDLERS']
    service_names = [reflection.SERVICE_NAME]
    for raw_handler in raw_handlers:
      handler = f'{raw_handler}.service_configuration'
      try:
        service_configuration = import_string(handler)
        service_configuration.register_service(self.server)
        service_names.append(service_configuration.name)
      except ImportError as error:
        raise ImportError(f'Could not import "{handler}" for gRPC handler.') from error
    reflection.enable_server_reflection(service_names, self.server)

  def _handle_sigterm(self, *_: Any) -> None :
    """Shutdown gracefully."""
    try:
      HEALTH_METRIC.set(value = HealthMetricType.TERMINATING)
      done_event = self.server.stop(30)
      if done_event.wait(30):
        self._log_server_state_event(
          action = Event.Action.ActionType.END,
          result = Event.Action.ResultType.SUCCESS,
          details = 'Server stopped successfully.'
        )
      else:
        self._log_server_state_event(
          action = Event.Action.ActionType.END,
          result = Event.Action.ResultType.ERROR,
          details = 'Server stop failed... timeout instead of graceful shutdown.',
        )
      self.channel_manager.close_all_channels()
    except Exception as exception:
      self._log_server_state_event(
        action = Event.Action.ActionType.END,
        result = Event.Action.ResultType.FATAL,
        details = f'Server stop failed... {type(exception).__name__}: {str(exception)}'
      )
      raise exception from None

  def _server_state_event(
      self, *,
      action: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
      details: str,
  ) -> Event :
    """Create the event for logging the server state."""
    event = Event()
    # Metadata.
    add_request_metadata(
      request      = event,
      request_id   = -1,  # Not handling a gRPC call.
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
    if result == Event.Action.ResultType.SUCCESS:
      LOGGER.info(message = details)
    elif result == Event.Action.ResultType.ERROR:
      LOGGER.error(message = details)
    elif result == Event.Action.ResultType.FATAL:
      LOGGER.fatal(message = details)
    event = self._server_state_event(action = action, result = result, details = details)
    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      channel = self.channel_manager.get_channel(gate = 'core', service = 'sawmill')
      stub = LumberjackStub(channel)  # type: ignore[no-untyped-call]
      stub.LogEvent(event)
    else:
      # Send directly to the DB. Note that Events must be present in the schema!
      from microservice.models import Event as DbEvent  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      DbEvent.objects.log_event(grpc_event = event)