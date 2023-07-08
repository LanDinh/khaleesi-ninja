"""Structured logger using gRPC."""

# khaleesi.ninja.
from khaleesi.core.logging.structuredLogger import StructuredLogger
from khaleesi.proto.core_pb2 import EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest,
  GrpcResponseRequest,
  Error,
  EventRequest,
  HttpRequest,
  HttpResponseRequest,
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

  def sendLogSystemHttpRequest(self, *, httpRequest: EmptyRequest) -> None:
    """Send the log request to the logging facility."""
    DbHttpRequest.objects.logSystemRequest(grpcRequest = httpRequest)

  def sendLogHttpRequest(self, *, httpRequest: HttpRequest) -> None:
    """Send the log request to the logging facility."""
    DbHttpRequest.objects.logRequest(grpcRequest = httpRequest)

  def sendLogHttpResponse(self, *, httpResponse: HttpResponseRequest) -> None :
    """Send the log response to the logging facility."""
    DbHttpRequest.objects.logResponse(grpcResponse = httpResponse)

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
      DbHttpRequest.objects.addChildDuration(request = result)
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

  def sendLogError(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    DbError.objects.logError(grpcError = error)

  def sendLogEvent(self, *, event: EventRequest) -> None :
    """Send the log event to the logging facility."""
    DbEvent.objects.khaleesiCreate(grpc = event)
