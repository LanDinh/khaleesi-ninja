"""Structured logger using gRPC."""
from typing import List

# khaleesi.ninja.
from khaleesi.core.logging.structuredLogger import StructuredLogger
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequestRequest,
  GrpcRequestRequest,
  ErrorRequest,
  EventRequest,
  QueryRequest,
  ResponseRequest,
)
from microservice.models.siteRegistry import SITE_REGISTRY
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
    return DbHttpRequest.objects.khaleesiCreate(grpc = grpc)

  def sendLogHttpResponse(self, *, grpc: ResponseRequest) -> DbHttpRequest :  # type: ignore[override]  # pylint: disable=line-too-long
    """Send the log response to the logging facility."""
    instance = DbHttpRequest.objects.get(
      metaCallerHttpRequestId = grpc.requestMetadata.httpCaller.requestId,
    )
    instance.finish(request = grpc)
    return instance

  def sendLogGrpcRequest(self, *, grpc: GrpcRequestRequest) -> DbGrpcRequest :  # type: ignore[override]  # pylint: disable=line-too-long
    """Send the log request to the logging facility."""
    instance = DbGrpcRequest.objects.khaleesiCreate(grpc = grpc)
    LOGGER.info('Adding call to site registry.')
    SITE_REGISTRY.addCall(
      callerDetails = grpc.request.upstreamRequest,
      calledDetails = grpc.requestMetadata.grpcCaller,
    )
    return instance

  def sendLogGrpcResponse(self, *, grpc: ResponseRequest) -> DbGrpcRequest :  # type: ignore[override]  # pylint: disable=line-too-long
    """Send the log response to the logging facility."""
    instance = DbGrpcRequest.objects.get(
      metaCallerGrpcRequestId = grpc.requestMetadata.grpcCaller.requestId,
    )
    # noinspection PyBroadException
    try:
      LOGGER.info('Adding the duration to the parent HTTP request.')
      dbHttpRequest = DbHttpRequest.objects.get(
        metaCallerHttpRequestId = grpc.requestMetadata.httpCaller.requestId,
      )
      dbHttpRequest.addChildDuration(duration = instance.reportedDuration)
      dbHttpRequest.khaleesiSave(
        metadata = dbHttpRequest.toObjectMetadata(),
        grpc     = dbHttpRequest.toGrpc(),
      )
    except Exception:  # pylint: disable=broad-except  # pragma: no cover
      # TODO(45) - remove this hack
      pass
    LOGGER.info('Saving the corresponding queries to the database.')
    errors = instance.metaLoggingErrors
    requestMetadata = instance.toGrpc().requestMetadata
    newQueries: List[DbQuery] = []
    for rawQuery in grpc.queries:
      grpcQuery = QueryRequest()
      grpcQuery.query.CopyFrom(rawQuery)
      grpcQuery.requestMetadata.CopyFrom(requestMetadata)
      # Don't save it - bulk creation.
      query = DbQuery.objects.khaleesiCreate(grpc = grpcQuery, update_fields = [])
      newQueries.append(query)
      errors += query.metaLoggingErrors
      instance.addChildDuration(duration = query.reportedDuration)
    DbQuery.objects.bulk_create(objs = newQueries, batch_size = 1000)
    instance.finish(request = grpc)
    instance.metaLoggingErrors = errors  # Don't save it, but it might need to be handled.
    return instance

  def sendLogEvent(self, *, grpc: EventRequest) -> DbEvent :  # type: ignore[override]
    """Send the log event to the logging facility."""
    return DbEvent.objects.khaleesiCreate(grpc = grpc)

  def sendLogError(self, *, grpc: ErrorRequest) -> DbError :  # type: ignore[override]
    """Send the log error to the logging facility."""
    return DbError.objects.khaleesiCreate(grpc = grpc)
