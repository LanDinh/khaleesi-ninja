"""The gRPC server."""

# Python.
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from signal import signal, SIGTERM
from typing import Any, List
from uuid import uuid4

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode, server, Server as GrpcServer
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
from khaleesi.core.shared.exceptions import (
  MaskingInternalServerException,
  KhaleesiException,
  TimeoutException,
)
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
# noinspection PyUnresolvedReferences
from microservice.metric_initializer import MetricInitializer


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Server:
  """The gRPC server."""

  server                   : GrpcServer
  health_servicer          : HealthServicer
  metric_initializer       : MetricInitializer
  service_names            : List[str]
  start_backgate_request_id: str

  def __init__(self, *, start_backgate_request_id: str, initialize_request_id: str) -> None :
    try:
      self.start_backgate_request_id = start_backgate_request_id
      LOGGER.info('Initializing metrics...')
      self.metric_initializer = MetricInitializer(backgate_request_id = start_backgate_request_id)
      self.metric_initializer.initialize_metrics()
      LOGGER.info('Initializing health servicer...')
      self.health_servicer = HealthServicer()
      LOGGER.info('Initializing server...')
      self.server = server(
        ThreadPoolExecutor(khaleesi_settings['GRPC']['THREADS']),
        interceptors = [
            instantiate_request_state_interceptor(),  # Outer.
            instantiate_prometheus_interceptor(),
            instantiate_logging_interceptor(),  # Inner.
        ],
      )
      LOGGER.info('Initializing configure server...')
      self.server.add_insecure_port(f'[::]:{khaleesi_settings["GRPC"]["PORT"]}')
      signal(SIGTERM, self._handle_sigterm)
      LOGGER.info('Adding service handlers...')
      self._init_add_handlers()
    except KhaleesiException as exception:
      self._log_start_exception(
        exception  = exception,
        request_id = initialize_request_id,
        activity   = 'initialization'
      )
      raise
    except Exception as exception:
      masked = MaskingInternalServerException(exception = exception)
      self._log_start_exception(
        exception  = masked,
        request_id = initialize_request_id,
        activity   = 'initialization'
      )
      raise masked from exception

  def start(self, *, start_request_id: str) -> None :
    """Start the server."""
    try:
      LOGGER.info('Starting server...')
      self.server.start()
      LOGGER.info('Setting health state...')
      for service_name in self.service_names:
        self.health_servicer.set(service_name, HealthCheckResponse.SERVING)  # type: ignore[arg-type]  # pylint: disable=line-too-long
      self.health_servicer.set('', HealthCheckResponse.SERVING)  # type: ignore[arg-type]
      self._log_server_start_event(
        request_id = start_request_id,
        result     = Event.Action.ResultType.SUCCESS,
        details    = 'Server started successfully.',
      )
    except KhaleesiException as exception:
      self._log_start_exception(
        exception  = exception,
        request_id = start_request_id,
        activity   = 'start'
      )
      raise
    except Exception as exception:
      masked = MaskingInternalServerException(exception = exception)
      self._log_start_exception(
        exception  = masked,
        request_id = start_request_id,
        activity   = 'start'
      )
      raise masked from exception

  def wait_for_termination(self) -> None :
    """Wait for termination. No more log messages will be called in this thread."""
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

  def _handle_sigterm(self, *_: Any) -> None :
    """Shutdown gracefully."""
    seconds_remaining = khaleesi_settings['GRPC']['SHUTDOWN_GRACE_SECS']
    end = datetime.now(tz = timezone.utc) + timedelta(seconds = seconds_remaining)
    stop_backgate_request_id = str(uuid4())
    request_id               = str(uuid4())

    try:
      SINGLETON.structured_logger.log_system_backgate_request(
        backgate_request_id = stop_backgate_request_id,
        grpc_method         = 'LIFECYCLE',
      )
      SINGLETON.structured_logger.log_system_request(
        backgate_request_id = stop_backgate_request_id,
        request_id          = request_id,
        grpc_method         = 'LIFECYCLE',
      )
      HEALTH_METRIC.set(value = HealthMetricType.TERMINATING)
      self.health_servicer.enter_graceful_shutdown()

      seconds_remaining = (end - datetime.now(tz = timezone.utc)).seconds
      done_event = self.server.stop(seconds_remaining)

      threads = JobExecution.objects.stop_all_jobs()
      for thread in threads:
        seconds_remaining = (end - datetime.now(tz = timezone.utc)).seconds
        thread.join(seconds_remaining)
      threads_finished_gracefully = True
      for thread in threads:
        if not thread.is_alive():
          threads_finished_gracefully = False

      seconds_remaining = (end - datetime.now(tz = timezone.utc)).seconds
      server_finished_gracefully = done_event.wait(seconds_remaining)

      if server_finished_gracefully and threads_finished_gracefully:
        self._log_server_state_event(
          backgate_request_id = stop_backgate_request_id,
          request_id          = request_id,
          action              = Event.Action.ActionType.END,
          result              = Event.Action.ResultType.SUCCESS,
          details             = 'Server stopped successfully.'
        )
        self._log_shutdown(
          backgate_request_id = stop_backgate_request_id,
          request_id          = request_id,
          status              = StatusCode.OK,
        )
        CHANNEL_MANAGER.close_all_channels()
        return

      reason = ''
      if not threads_finished_gracefully:
        reason += 'Threads didn\'t terminate. '
      if not server_finished_gracefully:
        reason += 'Server didn\'t terminate. '
      raise TimeoutException(private_details = f'Server stop timed out. - {reason}')
    except KhaleesiException as exception:
      self._log_end_exception(
        exception           = exception,
        action              = Event.Action.ActionType.END,
        backgate_request_id = stop_backgate_request_id,
        request_id          = request_id,
        activity            = 'stop',
      )
      raise
    except Exception as exception:
      masked = MaskingInternalServerException(exception = exception)
      self._log_end_exception(
        exception           = masked,
        action              = Event.Action.ActionType.END,
        backgate_request_id = stop_backgate_request_id,
        request_id          = request_id,
        activity            = 'stop',
      )
      raise

  def _log_start_exception(
      self, *,
      exception : KhaleesiException,
      request_id: str,
      activity  : str,
  ) -> None :
    """Log exceptions in the startup phase."""
    self._log_exception(
      exception           = exception,
      action              = Event.Action.ActionType.START,
      backgate_request_id = self.start_backgate_request_id,
      request_id          = request_id,
      activity            = activity
    )

  def _log_end_exception(
      self, *,
      exception          : KhaleesiException,
      action             : 'Event.Action.ActionType.V',
      backgate_request_id: str,
      request_id         : str,
      activity           : str,
  ) -> None :
    """Log exceptions when turning down the server."""
    self._log_exception(
      exception           = exception,
      action              = action,
      backgate_request_id = backgate_request_id,
      request_id          = request_id,
      activity            = activity,
    )
    self._log_shutdown(
      backgate_request_id = backgate_request_id,
      request_id          = request_id,
      status              = StatusCode.INTERNAL,
    )
    CHANNEL_MANAGER.close_all_channels()

  def _log_exception(
      self, *,
      exception          : KhaleesiException,
      action             : 'Event.Action.ActionType.V',
      backgate_request_id: str,
      request_id         : str,
      activity           : str,
  ) -> None :
    """Log exceptions."""
    SINGLETON.structured_logger.log_system_error(
      exception           = exception,
      backgate_request_id = backgate_request_id,
      request_id          = request_id,
      grpc_method         = 'LIFECYCLE'
    )
    self._log_server_state_event(
      backgate_request_id = backgate_request_id,
      request_id          = request_id,
      action              = action,
      result              = Event.Action.ResultType.FATAL,
      details = f'Server {activity} failed.'
                f' {exception.private_message}: {exception.private_details}',
    )

  def _log_server_start_event(
      self, *,
      request_id: str,
      result    : 'Event.Action.ResultType.V',
      details   : str,
  ) -> None :
    """Log the server state during the startup phase."""
    self._log_server_state_event(
      backgate_request_id = self.start_backgate_request_id,
      request_id          = request_id,
      action              = Event.Action.ActionType.START,
      result              = result,
      details             = details,
    )

  def _log_server_state_event(
      self, *,
      backgate_request_id: str,
      request_id         : str,
      action             : 'Event.Action.ActionType.V',
      result             : 'Event.Action.ResultType.V',
      details            : str,
  ) -> None :
    """Log the server state."""
    user = User()
    user.type = User.UserType.SYSTEM
    user.id = f'{khaleesi_settings["METADATA"]["GATE"]}-{khaleesi_settings["METADATA"]["SERVICE"]}'
    SINGLETON.structured_logger.log_system_event(
      backgate_request_id = backgate_request_id,
      request_id          = request_id,
      grpc_method         = 'LIFECYCLE',
      target              = khaleesi_settings['METADATA']['POD_ID'],
      owner               = user,
      action              = action,
      result              = result,
      details             = details,
      logger_send_metric  = True,
    )

  def _log_shutdown(
      self, *,
      backgate_request_id: str,
      request_id         : str,
      status             : StatusCode,
  ) -> None :
    """Log shutdown of server."""
    SINGLETON.structured_logger.log_system_response(
      backgate_request_id = backgate_request_id,
      request_id          = request_id,
      grpc_method         = 'LIFECYCLE',
      status              = status,
    )
    SINGLETON.structured_logger.log_system_backgate_response(
      backgate_request_id = backgate_request_id,
      grpc_method         = 'LIFECYCLE',
      status              = status,
    )
