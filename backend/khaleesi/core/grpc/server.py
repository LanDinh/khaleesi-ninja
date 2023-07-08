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
from khaleesi.core.batch.thread import stopAllJobs
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.core.grpc.importUtil import registerService
from khaleesi.core.interceptors.server.logging import instantiateLoggingInterceptor
from khaleesi.core.interceptors.server.prometheus import instantiatePrometheusInterceptor
from khaleesi.core.interceptors.server.requestState import instantiateRequestStateInterceptor
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.metrics.health import HEALTH as HEALTH_METRIC, HealthMetricType
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import (
  MaskingInternalServerException,
  KhaleesiException,
  TimeoutException,
)
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
# noinspection PyUnresolvedReferences
from microservice.metricInitializer import MetricInitializer


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class Server:
  """The gRPC server."""

  server              : GrpcServer
  healthServicer      : HealthServicer
  metricInitializer   : MetricInitializer
  serviceNames        : List[str]
  startHttpRequestId: str

  def __init__(self, *, startHttpRequestId: str, initializeGrpcRequestId: str) -> None :
    try:
      self.startHttpRequestId = startHttpRequestId
      LOGGER.info('Initializing metrics...')
      self.metricInitializer = MetricInitializer(httpRequestId = startHttpRequestId)
      self.metricInitializer.initializeMetrics()
      LOGGER.info('Initializing health servicer...')
      self.healthServicer = HealthServicer()
      LOGGER.info('Initializing server...')
      self.server = server(
        ThreadPoolExecutor(khaleesiSettings['GRPC']['THREADS']),
        interceptors = [
            instantiateRequestStateInterceptor(),  # Outer.
            instantiatePrometheusInterceptor(),
            instantiateLoggingInterceptor(),  # Inner.
        ],
      )
      LOGGER.info('Initializing configure server...')
      self.server.add_insecure_port(f'[::]:{khaleesiSettings["GRPC"]["PORT"]}')
      signal(SIGTERM, self._handleSigterm)
      LOGGER.info('Adding service handlers...')
      self._initAddHandlers()
    except KhaleesiException as exception:
      self._logStartException(
        exception     = exception,
        grpcRequestId = initializeGrpcRequestId,
        activity      = 'initialization'
      )
      raise
    except Exception as exception:
      masked = MaskingInternalServerException(exception = exception)
      self._logStartException(
        exception     = masked,
        grpcRequestId = initializeGrpcRequestId,
        activity      = 'initialization'
      )
      raise masked from exception

  def start(self, *, startGrpcRequestId: str) -> None :
    """Start the server."""
    try:
      LOGGER.info('Starting server...')
      self.server.start()
      LOGGER.info('Setting health state...')
      for serviceName in self.serviceNames:
        self.healthServicer.set(serviceName, HealthCheckResponse.SERVING)  # type: ignore[arg-type]
      self.healthServicer.set('', HealthCheckResponse.SERVING)  # type: ignore[arg-type]
      self._logServerStartEvent(
        grpcRequestId = startGrpcRequestId,
        result        = Event.Action.ResultType.SUCCESS,
        details       = 'Server started successfully.',
      )
    except KhaleesiException as exception:
      self._logStartException(
        exception     = exception,
        grpcRequestId = startGrpcRequestId,
        activity      = 'start'
      )
      raise
    except Exception as exception:
      masked = MaskingInternalServerException(exception = exception)
      self._logStartException(
        exception     = masked,
        grpcRequestId = startGrpcRequestId,
        activity      = 'start'
      )
      raise masked from exception

  def waitForTermination(self) -> None :
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

  def _initAddHandlers(self) -> None :
    """Attempt to import handlers from string representations."""
    rawHandlers = khaleesiSettings['GRPC']['HANDLERS']
    self.serviceNames = [reflection.SERVICE_NAME]
    for rawHandler in rawHandlers:
      self.serviceNames.append(registerService(rawHandler = rawHandler, server = self.server))
    LOGGER.debug('Adding reflection service...')
    reflection.enable_server_reflection(self.serviceNames, self.server)
    LOGGER.debug('Adding health service...')
    add_HealthServicer_to_server(self.healthServicer, self.server)

  def _handleSigterm(self, *_: Any) -> None :
    """Shutdown gracefully."""
    secondsRemaining  = khaleesiSettings['GRPC']['SHUTDOWN_GRACE_SECS']
    end               = datetime.now(tz = timezone.utc) + timedelta(seconds = secondsRemaining)
    stopHttpRequestId = str(uuid4())
    grpcRequestId     = str(uuid4())

    try:
      SINGLETON.structuredLogger.logSystemHttpRequest(
        httpRequestId = stopHttpRequestId,
        grpcMethod    = 'LIFECYCLE',
      )
      SINGLETON.structuredLogger.logSystemGrpcRequest(
        httpRequestId = stopHttpRequestId,
        grpcRequestId = grpcRequestId,
        grpcMethod    = 'LIFECYCLE',
      )
      HEALTH_METRIC.set(value = HealthMetricType.TERMINATING)
      self.healthServicer.enter_graceful_shutdown()

      secondsRemaining = (end - datetime.now(tz = timezone.utc)).seconds
      doneEvent = self.server.stop(secondsRemaining)

      threads = stopAllJobs()
      for thread in threads:
        secondsRemaining = (end - datetime.now(tz = timezone.utc)).seconds
        thread.join(secondsRemaining)
      threadsFinishedGracefully = True
      for thread in threads:
        if not thread.is_alive():
          threadsFinishedGracefully = False

      secondsRemaining         = (end - datetime.now(tz = timezone.utc)).seconds
      serverFinishedGracefully = doneEvent.wait(secondsRemaining)

      if serverFinishedGracefully and threadsFinishedGracefully:
        self._logServerStateEvent(
          httpRequestId = stopHttpRequestId,
          grpcRequestId = grpcRequestId,
          action        = Event.Action.ActionType.END,
          result        = Event.Action.ResultType.SUCCESS,
          details       = 'Server stopped successfully.'
        )
        self._logShutdown(
          httpRequestId = stopHttpRequestId,
          grpcRequestId = grpcRequestId,
          status        = StatusCode.OK,
        )
        CHANNEL_MANAGER.closeAllChannels()
        return

      reason = ''
      if not threadsFinishedGracefully:
        reason += 'Threads didn\'t terminate. '
      if not serverFinishedGracefully:
        reason += 'Server didn\'t terminate. '
      raise TimeoutException(privateDetails = f'Server stop timed out. - {reason}')
    except KhaleesiException as exception:
      self._logEndException(
        exception     = exception,
        action        = Event.Action.ActionType.END,
        httpRequestId = stopHttpRequestId,
        grpcRequestId = grpcRequestId,
        activity      = 'stop',
      )
      raise
    except Exception as exception:
      masked = MaskingInternalServerException(exception = exception)
      self._logEndException(
        exception     = masked,
        action        = Event.Action.ActionType.END,
        httpRequestId = stopHttpRequestId,
        grpcRequestId = grpcRequestId,
        activity      = 'stop',
      )
      raise

  def _logStartException(
      self, *,
      exception    : KhaleesiException,
      grpcRequestId: str,
      activity     : str,
  ) -> None :
    """Log exceptions in the startup phase."""
    self._logException(
      exception     = exception,
      action        = Event.Action.ActionType.START,
      httpRequestId = self.startHttpRequestId,
      grpcRequestId = grpcRequestId,
      activity      = activity
    )

  def _logEndException(
      self, *,
      exception    : KhaleesiException,
      action       : 'Event.Action.ActionType.V',
      httpRequestId: str,
      grpcRequestId: str,
      activity     : str,
  ) -> None :
    """Log exceptions when turning down the server."""
    self._logException(
      exception     = exception,
      action        = action,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      activity      = activity,
    )
    self._logShutdown(
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      status        = StatusCode.INTERNAL,
    )
    CHANNEL_MANAGER.closeAllChannels()

  def _logException(
      self, *,
      exception    : KhaleesiException,
      action       : 'Event.Action.ActionType.V',
      httpRequestId: str,
      grpcRequestId: str,
      activity     : str,
  ) -> None :
    """Log exceptions."""
    SINGLETON.structuredLogger.logSystemError(
      exception     = exception,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = 'LIFECYCLE'
    )
    self._logServerStateEvent(
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      action        = action,
      result        = Event.Action.ResultType.FATAL,
      details = f'Server {activity} failed.'
                f' {exception.privateMessage}: {exception.privateDetails}',
    )

  def _logServerStartEvent(
      self, *,
      grpcRequestId: str,
      result       : 'Event.Action.ResultType.V',
      details      : str,
  ) -> None :
    """Log the server state during the startup phase."""
    self._logServerStateEvent(
      httpRequestId = self.startHttpRequestId,
      grpcRequestId = grpcRequestId,
      action        = Event.Action.ActionType.START,
      result        = result,
      details       = details,
    )

  def _logServerStateEvent(
      self, *,
      httpRequestId: str,
      grpcRequestId: str,
      action       : 'Event.Action.ActionType.V',
      result       : 'Event.Action.ResultType.V',
      details      : str,
  ) -> None :
    """Log the server state."""
    grpcMethod = 'LIFECYCLE'
    metadataSettings = khaleesiSettings["METADATA"]
    event = Event()
    event.target.owner.type = User.UserType.SYSTEM
    event.target.owner.id   = f'{metadataSettings["GATE"]}-{metadataSettings["SERVICE"]}'
    event.target.id         = metadataSettings['POD_ID']
    event.target.type = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES'][grpcMethod]['TARGET']  # type: ignore[literal-required]  # pylint: disable=line-too-long
    event.action.crudType = action
    event.action.result   = result
    event.action.details  = details
    SINGLETON.structuredLogger.logSystemEvent(
      event         = event,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )

  def _logShutdown(
      self, *,
      httpRequestId: str,
      grpcRequestId: str,
      status       : StatusCode,
  ) -> None :
    """Log shutdown of server."""
    SINGLETON.structuredLogger.logSystemGrpcResponse(
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = 'LIFECYCLE',
      status        = status,
    )
    SINGLETON.structuredLogger.logSystemHttpResponse(
      httpRequestId = httpRequestId,
      grpcMethod    = 'LIFECYCLE',
      status        = status,
    )
