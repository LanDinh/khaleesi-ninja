"""Basic structured logger."""

# Python.
from abc import ABC, abstractmethod
from datetime import timezone, datetime
from typing import cast

# Django.
from django.conf import settings

# gRPC.
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.core.grpc.importUtil import importSetting
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.grpc.requestMetadata import addRequestMetadata, addSystemRequestMetadata
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequestRequest,
  ErrorRequest, GrpcRequest,
  GrpcResponseRequest,
  Event, EventRequest,
  ResponseRequest,
  Response,
  Query,
)
from khaleesi.proto.core_sawmill_pb2_grpc import LumberjackStub


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class StructuredLogger(ABC):
  """Basic structured logger."""

  def logHttpRequest(self, *, httpRequestId: str, grpcMethod: str) -> None :
    """Log a HTTP request for system requests."""
    LOGGER.info(
      f'System HTTP request "{httpRequestId}" started.'
    )
    httpRequest = HttpRequestRequest()
    addSystemRequestMetadata(
      metadata      = httpRequest.requestMetadata,
      grpcMethod    = grpcMethod,
      httpRequestId = httpRequestId,
      grpcRequestId = 'system',
    )
    self.sendLogHttpRequest(grpc = httpRequest)

  def logHttpResponse(
      self, *,
      httpRequestId: str,
      grpcMethod   : str,
      status       : StatusCode,
  ) -> None :
    """Log a microservice system HTTP response."""
    httpResponse = ResponseRequest()
    addSystemRequestMetadata(
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
    self.sendLogHttpResponse(grpc = httpResponse)

  def logEvent(self, *, event: Event) -> None :
    """Log a user event."""
    request = EventRequest()
    addRequestMetadata(metadata = request.requestMetadata)
    request.event.CopyFrom(event)
    self._logEvent(event = request)

  def logSystemEvent(
      self, *,
      event: Event,
      httpRequestId   : str,
      grpcRequestId   : str,
      grpcMethod      : str,
  ) -> None :
    """Log a system event."""
    request = EventRequest()
    addSystemRequestMetadata(
      metadata      = request.requestMetadata,
      grpcMethod    = grpcMethod,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
    )
    request.event.CopyFrom(event)
    self._logEvent(event = request)

  def logError(self, *, exception: KhaleesiException) -> None :
    """Log an exception."""
    error = self._logErrorObject(exception = exception)
    addRequestMetadata(metadata = error.requestMetadata)
    self.sendLogError(grpc = error)

  def logSystemError(
      self, *,
      exception    : KhaleesiException,
      httpRequestId: str,
      grpcRequestId: str,
      grpcMethod   : str,
  ) -> None :
    """Log an exception."""
    error = self._logErrorObject(exception = exception)
    addSystemRequestMetadata(
      metadata      = error.requestMetadata,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )
    self.sendLogError(grpc = error)

  def logGrpcRequest(self, *, upstreamRequest: RequestMetadata) -> None :
    """Log a microservice request."""
    LOGGER.info(
      f'User "{STATE.request.user.id}" started gRPC request '
      f'{STATE.request.grpcCaller.grpcService}.{STATE.request.grpcCaller.grpcMethod}.'
    )
    LOGGER.info(
      f'Upstream request "{upstreamRequest.grpcCaller.requestId}" caller data: '
      f'{upstreamRequest.grpcCaller.khaleesiGate}-{upstreamRequest.grpcCaller.khaleesiService}: '
      f'{upstreamRequest.grpcCaller.grpcService}.{upstreamRequest.grpcCaller.grpcMethod}'
    )

    grpcRequest = GrpcRequest()
    addRequestMetadata(metadata = grpcRequest.requestMetadata)
    grpcRequest.upstreamRequest.requestId       = upstreamRequest.grpcCaller.requestId
    grpcRequest.upstreamRequest.khaleesiGate    = upstreamRequest.grpcCaller.khaleesiGate
    grpcRequest.upstreamRequest.khaleesiService = upstreamRequest.grpcCaller.khaleesiService
    grpcRequest.upstreamRequest.grpcService     = upstreamRequest.grpcCaller.grpcService
    grpcRequest.upstreamRequest.grpcMethod      = upstreamRequest.grpcCaller.grpcMethod

    self.sendLogGrpcRequest(grpcRequest = grpcRequest)

  def logSystemGrpcRequest(
      self, *,
      httpRequestId: str,
      grpcRequestId: str,
      grpcMethod   : str,
  ) -> None :
    """Log a microservice request."""
    LOGGER.info(f'System started gRPC request "{grpcRequestId}".')
    grpcRequest = GrpcRequest()
    addSystemRequestMetadata(
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
    addSystemRequestMetadata(
      metadata      = grpcResponse.requestMetadata,
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
      grpcMethod    = grpcMethod,
    )
    self._logResponseObject(
      status      = status,
      requestName = 'gRPC Request',
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
      requestName = 'gRPC Request',
      response    = grpcResponse.response,
    )
    self._logQueries(queries = grpcResponse.queries)
    self.sendLogGrpcResponse(grpcResponse = grpcResponse)

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

  def _logEvent(self, *, event: EventRequest) -> None :
    """Log an event."""
    AUDIT_EVENT.inc(event = event)

    actionString = Event.Action.ActionType.Name(event.event.action.crudType) \
      if event.event.action.crudType else event.event.action.customType
    logString = \
      f'Event targeting "{event.event.target.type}": "{event.event.target.id}" owned by ' \
      f'"{event.event.target.owner.id}". ' \
      f'{actionString} with result {Event.Action.ResultType.Name(event.event.action.result)}.'

    if event.event.action.result == Event.Action.ResultType.SUCCESS:
      LOGGER.info(logString)
    elif event.event.action.result == Event.Action.ResultType.WARNING:
      LOGGER.warning(logString)
    elif event.event.action.result == Event.Action.ResultType.ERROR:
      LOGGER.error(logString)
    elif event.event.action.result == Event.Action.ResultType.FATAL:
      LOGGER.fatal(logString)
    else:
      LOGGER.fatal(logString)

    self.sendLogEvent(grpc = event)

  def _logErrorObject(self, *, exception: KhaleesiException) -> ErrorRequest :
    """Text log an exception and return the error object."""
    LOGGER.log(exception.toJson(), loglevel = exception.loglevel)
    LOGGER.log(exception.stacktrace, loglevel = exception.loglevel)
    error = ErrorRequest()
    error.error.status         = exception.status.name
    error.error.loglevel       = exception.loglevel.name
    error.error.gate           = exception.gate
    error.error.service        = exception.service
    error.error.publicKey      = exception.publicKey
    error.error.publicDetails  = exception.publicDetails
    error.error.privateMessage = exception.privateMessage
    error.error.privateDetails = exception.privateDetails
    error.error.stacktrace     = exception.stacktrace
    return error

  def _logQueries(self, *, queries: RepeatedCompositeFieldContainer[Query]) -> None :
    """Attach queries to the gRPC object."""
    count = 0
    for query in STATE.queries:
      queries.append(query)
      count += 1
    LOGGER.info(f'Reporting {count} queries.')

  @abstractmethod
  def sendLogHttpRequest(self, *, grpc: HttpRequestRequest) -> None :
    """Send the HTTP log request to the logging facility."""

  @abstractmethod
  def sendLogHttpResponse(self, *, grpc: ResponseRequest) -> None :
    """Send the HTTP log response to the logging facility."""

  @abstractmethod
  def sendLogGrpcRequest(self, *, grpcRequest: GrpcRequest) -> None :
    """Send the gRPC log request to the logging facility."""

  @abstractmethod
  def sendLogGrpcResponse(self, *, grpcResponse: GrpcResponseRequest) -> None :
    """Send the gRPC log response to the logging facility."""

  @abstractmethod
  def sendLogEvent(self, *, grpc: EventRequest) -> None :
    """Send the log event to the logging facility."""

  @abstractmethod
  def sendLogError(self, *, grpc: ErrorRequest) -> None :
    """Send the log error to the logging facility."""


class StructuredGrpcLogger(StructuredLogger):
  """Structured logger using gRPC."""

  stub: LumberjackStub

  def __init__(self) -> None :
    channel = CHANNEL_MANAGER.getChannel(gate = 'core', service = 'sawmill')
    self.stub = LumberjackStub(channel)  # type: ignore[no-untyped-call]

  def sendLogHttpRequest(self, *, grpc: HttpRequestRequest) -> None:
    """Send the HTTP log request to the logging facility."""
    self.stub.LogHttpRequest(grpc)

  def sendLogHttpResponse(self, *, grpc: ResponseRequest) -> None :
    """Send the HTTP log response to the logging facility."""
    self.stub.LogHttpRequestResponse(grpc)

  def sendLogGrpcRequest(self, *, grpcRequest: GrpcRequest) -> None :
    """Send the gRPC log request to the logging facility."""
    self.stub.LogGrpcRequest(grpcRequest)

  def sendLogGrpcResponse(self, *, grpcResponse: GrpcResponseRequest) -> None :
    """Send the gRPC log response to the logging facility."""
    self.stub.LogGrpcResponse(grpcResponse)

  def sendLogEvent(self, *, grpc: EventRequest) -> None :
    """Send the log event to the logging facility."""
    self.stub.LogEvent(grpc)

  def sendLogError(self, *, grpc: ErrorRequest) -> None :
    """Send the log error to the logging facility."""
    self.stub.LogError(grpc)


def instantiateStructuredLogger() -> StructuredLogger:
  """Instantiate the structured logger."""
  LOGGER.info('Importing structured logger...')
  return cast(StructuredLogger, importSetting(
    name               = 'structured logger',
    fullyQualifiedName = khaleesiSettings['GRPC']['INTERCEPTORS']['STRUCTURED_LOGGER']['NAME'],
  ))
