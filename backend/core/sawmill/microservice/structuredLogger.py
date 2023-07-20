"""Structured logger using gRPC."""

# khaleesi.ninja.
from khaleesi.core.logging.structuredLogger import StructuredLogger
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequestRequest,
  GrpcRequestRequest,
  ErrorRequest,
  EventRequest,
  ResponseRequest,
)
from microservice.models.serviceRegistry import SERVICE_REGISTRY
from microservice.models import (
  GrpcRequest as DbGrpcRequest,
  Error as DbError,
  Event as DbEvent,
  HttpRequest as DbHttpRequest,
  Query as DbQuery,
)


class StructuredDbLogger(StructuredLogger):
  """Structured logger using gRPC."""

  def sendLogHttpRequest(self, *, grpc: HttpRequestRequest) -> DbHttpRequest:  # type: ignore[override]  # pylint: disable=line-too-long
    """Send the log request to the logging facility."""
    instance = DbHttpRequest()
    instance.khaleesiSave(grpc = grpc)
    return instance

  def sendLogHttpResponse(self, *, grpc: ResponseRequest) -> DbHttpRequest :  # type: ignore[override]  # pylint: disable=line-too-long
    """Send the log response to the logging facility."""
    instance = DbHttpRequest.objects.get(
      metaCallerHttpRequestId = grpc.requestMetadata.httpCaller.requestId,
    )
    instance.finish(request = grpc)
    return instance

  def sendLogGrpcRequest(self, *, grpc: GrpcRequestRequest) -> DbGrpcRequest :  # type: ignore[override]  # pylint: disable=line-too-long
    """Send the log request to the logging facility."""
    instance = DbGrpcRequest()
    instance.khaleesiSave(grpc = grpc)
    LOGGER.info('Adding call to service registry.')
    SERVICE_REGISTRY.addCall(
      callerDetails = grpc.request.upstreamRequest,
      calledDetails = grpc.requestMetadata.grpcCaller,
    )
    return instance

  def sendLogGrpcResponse(self, *, grpc: ResponseRequest) -> DbGrpcRequest :  # type: ignore[override]  # pylint: disable=line-too-long
    """Send the log response to the logging facility."""
    instance = DbGrpcRequest.objects.get(
      metaCallerGrpcRequestId = grpc.requestMetadata.grpcCaller.requestId,
    )
    instance.finish(request = grpc)
    # noinspection PyBroadException
    try:
      LOGGER.info('Adding the duration to the parent HTTP request.')
      dbHttpRequest = DbHttpRequest.objects.get(
        metaCallerHttpRequestId = grpc.requestMetadata.httpCaller.requestId,
      )
      dbHttpRequest.addChildDuration(duration = instance.reportedDuration)
      dbHttpRequest.khaleesiSave(grpc = dbHttpRequest.toGrpc())
    except Exception:  # pylint: disable=broad-except  # pragma: no cover
      # TODO(45) - remove this hack
      pass
    LOGGER.info('Saving the corresponding queries to the database.')
    queries = DbQuery.objects.logQueries(
      queries  = grpc.queries,
      metadata = instance.toGrpc().requestMetadata,
    )
    LOGGER.info('Handling query errors and query duration.')
    errors = instance.metaLoggingErrors
    for query in queries:
      errors += query.metaLoggingErrors
      instance.metaChildDuration += query.reportedDuration
    instance.khaleesiSave(grpc = instance.toGrpc())
    instance.metaLoggingErrors = errors  # Don't save it, but it might need to be handled.
    return instance

  def sendLogEvent(self, *, grpc: EventRequest) -> DbEvent :  # type: ignore[override]
    """Send the log event to the logging facility."""
    instance = DbEvent()
    instance.khaleesiSave(grpc = grpc)
    return instance

  def sendLogError(self, *, grpc: ErrorRequest) -> DbError :  # type: ignore[override]
    """Send the log error to the logging facility."""
    instance = DbError()
    instance.khaleesiSave(grpc = grpc)
    return instance
