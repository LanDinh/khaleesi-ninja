"""Basic structured logger."""

# Python.
from abc import ABC, abstractmethod
from datetime import timezone, datetime
from typing import cast

# Django.
from uuid import uuid4

from django.conf import settings

# gRPC.
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.core.grpc.importUtil import importSetting
from khaleesi.core.grpc.requestMetadata import (
  addRequestMetadata,
  addGrpcServerSystemRequestMetadata,
)
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest,
  GrpcResponseRequest,
  Error,
  Event,
  EmptyRequest,
  HttpRequest,
  HttpResponseRequest,
  Response,
  Query,
)
from khaleesi.proto.core_sawmill_pb2_grpc import LumberjackStub


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class StructuredLogger(ABC):
  """Basic structured logger."""

  def logGrpcRequest(self, *, upstreamRequest: RequestMetadata) -> None :
    """Log a microservice request."""
    LOGGER.info(
      f'User "{STATE.user.userId}" started request '
      f'{STATE.request.grpcService}.{STATE.request.grpcMethod}.'
    )
    LOGGER.info(
      f'Upstream request "{upstreamRequest.caller.grpcRequestId}" caller data: '
      f'{upstreamRequest.caller.khaleesiGate}-{upstreamRequest.caller.khaleesiService}: '
      f'{upstreamRequest.caller.grpcService}.{upstreamRequest.caller.grpcMethod}'
    )

    grpcRequest = GrpcRequest()
    addRequestMetadata(metadata = grpcRequest.requestMetadata)
    grpcRequest.upstreamRequest.grpcRequestId   = upstreamRequest.caller.grpcRequestId
    grpcRequest.upstreamRequest.khaleesiGate    = upstreamRequest.caller.khaleesiGate
    grpcRequest.upstreamRequest.khaleesiService = upstreamRequest.caller.khaleesiService
    grpcRequest.upstreamRequest.grpcService     = upstreamRequest.caller.grpcService
    grpcRequest.upstreamRequest.grpcMethod      = upstreamRequest.caller.grpcMethod

    self.sendLogGrpcRequest(grpcRequest = grpcRequest)

  def logSystemGrpcRequest(
      self, *,
      httpRequestId: str,
      grpcRequestId: str,
      grpcMethod   : str,
  ) -> None :
    """Log a microservice request."""
    LOGGER.info(f'System started request "{grpcRequestId}".')
    grpcRequest = GrpcRequest()
    addGrpcServerSystemRequestMetadata(
      metadata      = grpcRequest.requestMetadata,
      grpcMethod    = grpcMethod,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
    )
    self.sendLogGrpcRequest(grpcRequest = grpcRequest)

  def logSystemGrpcResponse(
      self, *,
      httpRequestId: str,
      grpcRequestId: str,
      grpcMethod   : str,
      status       : StatusCode,
  ) -> None :
    """Log a microservice system response."""
    grpcResponse = GrpcResponseRequest()
    addGrpcServerSystemRequestMetadata(
      metadata      = grpcResponse.requestMetadata,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )
    self._logResponseObject(
      status      = status,
      requestName = 'Request',
      response    = grpcResponse.response,
    )
    self._logQueries(queries = grpcResponse.queries)
    self.sendLogGrpcResponse(grpcResponse = grpcResponse)

  def logGrpcResponse(self, *, status: StatusCode) -> None :
    """Log a microservice response."""
    grpcResponse = GrpcResponseRequest()
    addRequestMetadata(metadata = grpcResponse.requestMetadata)
    self._logResponseObject(
      status      = status,
      requestName = 'Request',
      response    = grpcResponse.response,
    )
    self._logQueries(queries = grpcResponse.queries)
    self.sendLogGrpcResponse(grpcResponse = grpcResponse)

  def logError(self, *, exception: KhaleesiException) -> None :
    """Log an exception."""
    error = self._logErrorObject(exception = exception)
    addRequestMetadata(metadata = error.requestMetadata)
    self.sendLogError(error = error)

  def logSystemError(
      self, *,
      exception    : KhaleesiException,
      httpRequestId: str,
      grpcRequestId: str,
      grpcMethod   : str,
  ) -> None :
    """Log an exception."""
    error = self._logErrorObject(exception = exception)
    addGrpcServerSystemRequestMetadata(
      metadata      = error.requestMetadata,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )
    self.sendLogError(error = error)

  def logSystemHttpRequest(self, *, httpRequestId: str, grpcMethod: str) -> None :
    """Log a HTTP request for system requests."""
    LOGGER.info(
      f'HTTP request "{httpRequestId}" started.'
    )
    httpRequest = EmptyRequest()
    addGrpcServerSystemRequestMetadata(
      metadata      = httpRequest.requestMetadata,
      grpcMethod    = grpcMethod,
      httpRequestId = httpRequestId,
      grpcRequestId = 'system',
    )
    self.sendLogSystemHttpRequest(httpRequest = httpRequest)

  def logHttpRequest(self) -> None :
    """Log a HTTP request for system requests."""
    LOGGER.info(f'HTTP request "{STATE.request.httpRequestId}" started.')
    httpRequest = HttpRequest()
    addRequestMetadata(metadata = httpRequest.requestMetadata)
    self.sendLogHttpRequest(httpRequest = httpRequest)

  def logSystemHttpResponse(
      self, *,
      httpRequestId: str,
      grpcMethod   : str,
      status       : StatusCode,
  ) -> None :
    """Log a microservice system HTTP response."""
    httpResponse = HttpResponseRequest()
    addGrpcServerSystemRequestMetadata(
      metadata      = httpResponse.requestMetadata,
      grpcMethod    = grpcMethod,
      httpRequestId = httpRequestId,
      grpcRequestId = 'system',
    )
    self._logResponseObject(
      status      = status,
      requestName = f'HTTP request "{httpRequestId}"',
      response    = httpResponse.response,
    )
    self.sendLogHttpResponse(httpResponse = httpResponse)

  def logHttpResponse(self, *, status: StatusCode) -> None :
    """Log a microservice HTTP response."""
    httpResponse = HttpResponseRequest()
    addRequestMetadata(metadata = httpResponse.requestMetadata)
    self._logResponseObject(
      status      = status,
      requestName = f'HTTP request "{STATE.request.httpRequestId}"',
      response    = httpResponse.response,
    )
    self.sendLogHttpResponse(httpResponse = httpResponse)

  def logSystemEvent(
      self, *,
      httpRequestId   : str,
      grpcRequestId   : str,
      grpcMethod      : str,
      target          : str,
      owner           : User,
      action          : 'Event.Action.ActionType.V',
      result          : 'Event.Action.ResultType.V',
      details         : str,
      loggerSendMetric: bool,
  ) -> None :
    """Log a system event."""
    event = Event()
    addGrpcServerSystemRequestMetadata(
      metadata      = event.requestMetadata,
      grpcMethod    = grpcMethod,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
    )
    self._logEvent(
      event            = event,
      target           = target,
      targetType       = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES'][grpcMethod]['TARGET'],  # type: ignore[literal-required]  # pylint: disable=line-too-long
      owner            = owner,
      action           = '',
      actionCrud       = action,
      result           = result,
      details          = details,
      loggerSendMetric = loggerSendMetric,
    )

  def logEvent(
      self, *,
      target    : str,
      targetType: str,
      owner     : User,
      action    : str,
      actionCrud: 'Event.Action.ActionType.V',
      result    : 'Event.Action.ResultType.V',
      details   : str,
  ) -> None :
    """Log a system event."""
    event = Event()
    addRequestMetadata(metadata = event.requestMetadata)
    self._logEvent(
      event            = event,
      target           = target,
      targetType       = targetType,
      owner            = owner,
      action           = action,
      actionCrud       = actionCrud,
      result           = result,
      details          = details,
      loggerSendMetric = False,
    )

  def _logEvent(
      self, *,
      event           : Event,
      target          : str,
      targetType      : str,
      owner           : User,
      action          : str,
      actionCrud      : 'Event.Action.ActionType.V',
      result          : 'Event.Action.ResultType.V',
      details         : str,
      loggerSendMetric: bool,
  ) -> None :
    """Log an event."""
    actionString = Event.Action.ActionType.Name(actionCrud) if actionCrud else action
    logString = \
      f'Event targeting "{targetType}": "{target}" owned by "{owner.id}". ' \
      f'{actionString} with result {Event.Action.ResultType.Name(result)}.'

    if result == Event.Action.ResultType.SUCCESS:
      LOGGER.info(logString)
    elif result == Event.Action.ResultType.WARNING:
      LOGGER.warning(logString)
    elif result == Event.Action.ResultType.ERROR:
      LOGGER.error(logString)
    elif result == Event.Action.ResultType.FATAL:
      LOGGER.fatal(logString)
    else:
      LOGGER.fatal(logString)

    event.id                = str(uuid4())
    event.target.type       = targetType
    event.target.id         = target
    event.target.owner.id   = owner.id
    event.target.owner.type = owner.type
    event.action.customType = action
    event.action.crudType   = actionCrud
    event.action.result     = result
    event.action.details    = details
    event.loggerSendMetric  = loggerSendMetric

    self.sendLogEvent(event = event)

  def _logQueries(self, *, queries: RepeatedCompositeFieldContainer[Query]) -> None :
    """Attach queries to the gRPC object."""
    count = 0
    for connection, stateQueries in STATE.queries.items():
      for query in stateQueries:
        grpcQuery            = queries.add()
        grpcQuery.id         = query.queryId
        grpcQuery.connection = connection
        grpcQuery.raw        = query.raw
        grpcQuery.start.FromDatetime(query.start)
        grpcQuery.end.FromDatetime(query.end)
        count += 1
    LOGGER.info(f'Reporting {count} queries.')

  def _logResponseObject(
      self, *,
      status     : StatusCode,
      requestName: str,
      response   : Response,
  ) -> None :
    """Text log a response and return the response object."""
    if status == StatusCode.OK:
      LOGGER.info(f'{requestName} finished successfully.')
    else:
      LOGGER.warning(f'{requestName} finished with error code {status.name}.')

    response.status = status.name
    response.timestamp.FromDatetime(datetime.now(tz = timezone.utc))

  def _logErrorObject(self, *, exception: KhaleesiException) -> Error :
    """Text log an exception and return the error object."""
    LOGGER.log(exception.toJson(), loglevel = exception.loglevel)
    LOGGER.log(exception.stacktrace, loglevel = exception.loglevel)
    error = Error()
    error.id             = str(uuid4())
    error.status         = exception.status.name
    error.loglevel       = exception.loglevel.name
    error.gate           = exception.gate
    error.service        = exception.service
    error.publicKey      = exception.publicKey
    error.publicDetails  = exception.publicDetails
    error.privateMessage = exception.privateMessage
    error.privateDetails = exception.privateDetails
    error.stacktrace     = exception.stacktrace
    return error

  @abstractmethod
  def sendLogSystemHttpRequest(self, *, httpRequest: EmptyRequest) -> None :
    """Send the HTTP log request to the logging facility."""

  @abstractmethod
  def sendLogHttpRequest(self, *, httpRequest: HttpRequest) -> None :
    """Send the HTTP log request to the logging facility."""

  @abstractmethod
  def sendLogHttpResponse(self, *, httpResponse: HttpResponseRequest) -> None :
    """Send the HTTP log response to the logging facility."""

  @abstractmethod
  def sendLogGrpcRequest(self, *, grpcRequest: GrpcRequest) -> None :
    """Send the gRPC log request to the logging facility."""

  @abstractmethod
  def sendLogGrpcResponse(self, *, grpcResponse: GrpcResponseRequest) -> None :
    """Send the gRPC log response to the logging facility."""

  @abstractmethod
  def sendLogError(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""

  @abstractmethod
  def sendLogEvent(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""


class StructuredGrpcLogger(StructuredLogger):
  """Structured logger using gRPC."""

  stub: LumberjackStub

  def __init__(self) -> None :
    channel = CHANNEL_MANAGER.getChannel(gate = 'core', service = 'sawmill')
    self.stub = LumberjackStub(channel)  # type: ignore[no-untyped-call]

  def sendLogSystemHttpRequest(self, *, httpRequest: EmptyRequest) -> None:
    """Send the HTTP log request to the logging facility."""
    self.stub.LogSystemHttpRequest(httpRequest)

  def sendLogHttpRequest(self, *, httpRequest: HttpRequest) -> None:
    """Send the HTTP log request to the logging facility."""
    self.stub.LogHttpRequest(httpRequest)

  def sendLogHttpResponse(self, *, httpResponse: HttpResponseRequest) -> None :
    """Send the HTTP log response to the logging facility."""
    self.stub.LogHttpRequestResponse(httpResponse)

  def sendLogGrpcRequest(self, *, grpcRequest: GrpcRequest) -> None :
    """Send the gRPC log request to the logging facility."""
    self.stub.LogGrpcRequest(grpcRequest)

  def sendLogGrpcResponse(self, *, grpcResponse: GrpcResponseRequest) -> None :
    """Send the gRPC log response to the logging facility."""
    self.stub.LogGrpcResponse(grpcResponse)

  def sendLogError(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    self.stub.LogError(error)

  def sendLogEvent(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    self.stub.LogEvent(event)


def instantiateStructuredLogger() -> StructuredLogger:
  """Instantiate the structured logger."""
  LOGGER.info('Importing structured logger...')
  return cast(StructuredLogger, importSetting(
    name               = 'structured logger',
    fullyQualifiedName = khaleesiSettings['GRPC']['INTERCEPTORS']['STRUCTURED_LOGGER']['NAME'],
  ))
