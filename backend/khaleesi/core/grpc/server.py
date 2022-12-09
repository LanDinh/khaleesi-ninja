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
from grpc_health.v1.health import HealthServicer
from grpc_health.v1.health_pb2 import HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import add_HealthServicer_to_server
from grpc_reflection.v1alpha import reflection

# khaleesi.ninja.
from khaleesi.core.grpc.channels import ChannelManager
from khaleesi.core.interceptors.server.logging import LoggingServerInterceptor
from khaleesi.core.interceptors.server.prometheus import PrometheusServerInterceptor
from khaleesi.core.interceptors.server.request_state import RequestStateServerInterceptor
from khaleesi.core.metrics.health import HEALTH as HEALTH_METRIC, HealthMetricType
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.logger import LOGGER
from khaleesi.core.shared.structured_logger import StructuredLogger
from khaleesi.proto.core_sawmill_pb2 import Event
# noinspection PyUnresolvedReferences
from metric_initializer import MetricInitializer


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Server:
  """The gRPC server."""

  server: GrpcServer
  channel_manager: ChannelManager
  health_servicer: HealthServicer
  structured_logger: StructuredLogger

  def __init__(self) -> None :
    try:
      LOGGER.info('Initializing channel manager...')
      self.channel_manager = ChannelManager()
      LOGGER.info('Initializing structured logger...')
      self._init_structured_logger()
      LOGGER.info('Initializing interceptors...')
      interceptors = [
          RequestStateServerInterceptor(),  # Outer.
          PrometheusServerInterceptor(),
          LoggingServerInterceptor(structured_logger = self.structured_logger),  # Inner.
      ]
      LOGGER.info('Initializing metric initializer...')
      self.metric_initializer = MetricInitializer(channel_manager = self.channel_manager)
      LOGGER.info('Initializing server...')
      self.server = server(
        ThreadPoolExecutor(khaleesi_settings['GRPC']['THREADS']),
        interceptors = interceptors,  # type: ignore[arg-type]  # fixed upstream!
      )
      LOGGER.info('Initializing health servicer...')
      self.health_servicer = HealthServicer()
      LOGGER.info('Initializing configure server...')
      self.server.add_insecure_port(f'[::]:{khaleesi_settings["GRPC"]["PORT"]}')
      signal(SIGTERM, self._handle_sigterm)
      LOGGER.info('Adding service handlers...')
      self._init_add_handlers()
    except Exception as exception:
      self._log_server_state_event(
        action = Event.Action.ActionType.START,
        result = Event.Action.ResultType.FATAL,
        details = f'Server start failed. {type(exception).__name__}: {str(exception)}'
      )
      raise

  def start(self) -> None :
    """Start the server."""
    try:
      LOGGER.info('Initializing metrics...')
      self.metric_initializer.initialize_metrics()
      LOGGER.info('Starting server...')
      self.server.start()
      self.health_servicer.set('', HealthCheckResponse.SERVING)  # type: ignore[arg-type]
      self._log_server_state_event(
        action = Event.Action.ActionType.START,
        result = Event.Action.ResultType.SUCCESS,
        details = 'Server started successfully.'
      )
      self._print_banner()
    except Exception as exception:
      self._log_server_state_event(
        action = Event.Action.ActionType.START,
        result = Event.Action.ResultType.FATAL,
        details = f'Server start failed. {type(exception).__name__}: {str(exception)}'
      )
      raise
    self.server.wait_for_termination()

  def _init_add_handlers(self) -> None :
    """Attempt to import handlers from string representations."""
    raw_handlers = khaleesi_settings['GRPC']['HANDLERS']
    service_names = [reflection.SERVICE_NAME]
    for raw_handler in raw_handlers:
      LOGGER.debug(f'Adding service handler {raw_handler}...')
      handler = f'{raw_handler}.service_configuration'
      try:
        service_configuration = import_string(handler)
        service_configuration.register_service(self.server)
        service_names.append(service_configuration.name)
      except ImportError as error:  # pragma: no cover
        raise ImportError(f'Could not import "{handler}" as gRPC handler.') from error
    LOGGER.debug('Adding reflection service...')
    reflection.enable_server_reflection(service_names, self.server)
    LOGGER.debug('Adding health service...')
    add_HealthServicer_to_server(self.health_servicer, self.server)
    for service_name in service_names:
      self.health_servicer.set(service_name, HealthCheckResponse.SERVING)  # type: ignore[arg-type]

  def _init_structured_logger(self) -> None :
    """Attempt to import the structured logger from string representations."""
    structured_logger = \
        khaleesi_settings['GRPC']['INTERCEPTORS']['LOGGING_SERVER_INTERCEPTOR']['STRUCTURED_LOGGER']
    LOGGER.debug(f'Adding structured logger {structured_logger}...')
    try:
      self.structured_logger = import_string(structured_logger)(
        channel_manager = self.channel_manager,
      )
    except ImportError as error:  # pragma: no cover
      raise ImportError(f'Could not import "{structured_logger}" as structured logger.') from error

  def _print_banner(self) -> None :
    """Print the startup banner."""
    LOGGER.info('')
    LOGGER.info('       \\****__              ____')
    LOGGER.info('         |    *****\\_      --/ *\\-__')
    LOGGER.info('         /_          (_    ./ ,/----\'')
    LOGGER.info('           \\__         (_./  /')
    LOGGER.info('              \\__           \\___----^__')
    LOGGER.info('               _/   _                  \\')
    LOGGER.info('        |    _/  __/ )\\"\\ _____         *\\')
    LOGGER.info('        |\\__/   /    ^ ^       \\____      )')
    LOGGER.info('         \\___--"                    \\_____ )')
    LOGGER.info('                                          "')
    LOGGER.info('')

  def _handle_sigterm(self, *_: Any) -> None :
    """Shutdown gracefully."""
    try:
      HEALTH_METRIC.set(value = HealthMetricType.TERMINATING)
      self.health_servicer.enter_graceful_shutdown()
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
      raise

  def _log_server_state_event(
      self, *,
      action: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log the server state."""
    self.structured_logger.log_system_event(
      grpc_method = 'LIFECYCLE',
      action = action,
      result = result,
      details = details,
    )
