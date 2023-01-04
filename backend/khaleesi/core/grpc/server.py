"""The gRPC server."""

# Python.
from concurrent.futures import ThreadPoolExecutor
from signal import signal, SIGTERM
from typing import Any, List
from uuid import uuid4

# Django.
from django.conf import settings

# gRPC.
from grpc import server, Server as GrpcServer, StatusCode
from grpc_health.v1.health import HealthServicer
from grpc_health.v1.health_pb2 import HealthCheckResponse
from grpc_health.v1.health_pb2_grpc import add_HealthServicer_to_server
from grpc_reflection.v1alpha import reflection

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.core.grpc.import_util import register_service
from khaleesi.core.interceptors.server.logging import instantiate_logging_interceptor
from khaleesi.core.interceptors.server.prometheus import instantiate_prometheus_interceptor
from khaleesi.core.interceptors.server.request_state import instantiate_request_state_interceptor
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.metrics.health import HEALTH as HEALTH_METRIC, HealthMetricType
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
# noinspection PyUnresolvedReferences
from microservice.metric_initializer import MetricInitializer


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Server:
  """The gRPC server."""

  server                      : GrpcServer
  health_servicer             : HealthServicer
  metric_initializer          : MetricInitializer
  service_names               : List[str]
  lifetime_backgate_request_id: str
  lifetime_request_id         : str

  def __init__(self) -> None :
    try:
      self._log_server_request_start()
      LOGGER.info('Initializing metric initializer...')
      self.metric_initializer = MetricInitializer(
        backgate_request_id = self.lifetime_backgate_request_id,
      )
      LOGGER.info('Initializing server...')
      self.server = server(
        ThreadPoolExecutor(khaleesi_settings['GRPC']['THREADS']),
        interceptors = [
            instantiate_request_state_interceptor(),  # Outer.
            instantiate_prometheus_interceptor(),
            instantiate_logging_interceptor(),  # Inner.
        ],
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
      LOGGER.info('Setting health state...')
      for service_name in self.service_names:
        self.health_servicer.set(service_name, HealthCheckResponse.SERVING)  # type: ignore[arg-type]  # pylint: disable=line-too-long
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
    # Use different IDs while the server is running.
    self.lifetime_backgate_request_id = str(uuid4())
    self.lifetime_request_id          = str(uuid4())
    self.server.wait_for_termination()

  def _init_add_handlers(self) -> None :
    """Attempt to import handlers from string representations."""
    raw_handlers = khaleesi_settings['GRPC']['HANDLERS']
    self.service_names = [reflection.SERVICE_NAME]
    for raw_handler in raw_handlers:
      self.service_names.append(register_service(raw_handler = raw_handler, server = self.server))
    LOGGER.debug('Adding reflection service...')
    reflection.enable_server_reflection(self.service_names, self.server)
    LOGGER.debug('Adding health service...')
    add_HealthServicer_to_server(self.health_servicer, self.server)

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
      self._log_server_request_start()
      HEALTH_METRIC.set(value = HealthMetricType.TERMINATING)
      self.health_servicer.enter_graceful_shutdown()
      done_event = self.server.stop(30)
      if done_event.wait(khaleesi_settings['GRPC']['SHUTDOWN_GRACE_SECS']):
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
      CHANNEL_MANAGER.close_all_channels()
    except Exception as exception:
      self._log_server_state_event(
        action = Event.Action.ActionType.END,
        result = Event.Action.ResultType.FATAL,
        details = f'Server stop failed... {type(exception).__name__}: {str(exception)}'
      )
      raise

  def _log_server_request_start(self) -> None :
    self.lifetime_backgate_request_id = str(uuid4())
    self.lifetime_request_id = str(uuid4())
    SINGLETON.structured_logger.log_system_backgate_request(
      backgate_request_id = self.lifetime_backgate_request_id,
      grpc_method         = 'LIFECYCLE',
    )
    SINGLETON.structured_logger.log_system_request(
      backgate_request_id = self.lifetime_backgate_request_id,
      request_id          = self.lifetime_request_id,
      grpc_method         = 'LIFECYCLE',
    )

  def _log_server_state_event(
      self, *,
      action: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log the server state."""
    user = User()
    user.type = User.UserType.SYSTEM
    user.id = f'{khaleesi_settings["METADATA"]["GATE"]}-{khaleesi_settings["METADATA"]["SERVICE"]}'
    SINGLETON.structured_logger.log_system_event(
      backgate_request_id = self.lifetime_backgate_request_id,
      request_id          = self.lifetime_request_id,
      grpc_method         = 'LIFECYCLE',
      target              = khaleesi_settings['METADATA']['POD_ID'],
      owner               = user,
      action              = action,
      result              = result,
      details             = details,
      logger_send_metric  = True,
    )
    status = StatusCode.OK if result == Event.Action.ResultType.SUCCESS else StatusCode.INTERNAL
    SINGLETON.structured_logger.log_response(request_id = self.lifetime_request_id, status = status)
    SINGLETON.structured_logger.log_backgate_response(
      backgate_request_id = self.lifetime_backgate_request_id,
      status = status,
    )
