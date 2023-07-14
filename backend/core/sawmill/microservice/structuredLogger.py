"""Structured logger using gRPC."""

# khaleesi.ninja.
from khaleesi.core.logging.structuredLogger import StructuredLogger
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequestRequest,
  GrpcRequest,
  GrpcResponseRequest,
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

  def sendLogHttpRequest(self, *, grpc: HttpRequestRequest) -> None:
    """Send the log request to the logging facility."""
    dbRequest = DbHttpRequest()
    dbRequest.khaleesiSave(grpc = grpc)

  def sendLogHttpResponse(self, *, grpc: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    dbRequest = DbHttpRequest.objects.get(
      metaCallerHttpRequestId = grpc.requestMetadata.httpCaller.requestId,
    )
    dbRequest.finish(request = grpc)

  def sendLogGrpcRequest(self, *, grpcRequest: GrpcRequest) -> None :
    """Send the log request to the logging facility."""
    DbGrpcRequest.objects.logRequest(grpcRequest = grpcRequest)
    SERVICE_REGISTRY.addCall(
      callerDetails = grpcRequest.upstreamRequest,
      calledDetails = grpcRequest.requestMetadata.grpcCaller,
    )

  def sendLogGrpcResponse(self, *, grpcResponse: GrpcResponseRequest) -> None :
    """Send the log response to the logging facility."""
    result = DbGrpcRequest.objects.logResponse(grpcResponse = grpcResponse)
    # noinspection PyBroadException
    try:
      dbHttpRequest = DbHttpRequest.objects.get(
        metaCallerHttpRequestId = grpcResponse.requestMetadata.httpCaller.requestId,
      )
      dbHttpRequest.addChildDuration(request = result)
    except Exception:  # pylint: disable=broad-except  # pragma: no cover
      # TODO(45) - remove this hack
      pass

    queries = DbQuery.objects.logQueries(
      queries  = grpcResponse.queries,
      metadata = result.toGrpc().request.requestMetadata,
    )
    for query in queries:
      result.metaChildDuration += query.reportedDuration
    result.save()

  def sendLogEvent(self, *, grpc: EventRequest) -> None :
    """Send the log event to the logging facility."""
    dbEvent = DbEvent()
    dbEvent.khaleesiSave(grpc = grpc)

  def sendLogError(self, *, grpc: ErrorRequest) -> None :
    """Send the log error to the logging facility."""
    dbError = DbError()
    dbError.khaleesiSave(grpc = grpc)
