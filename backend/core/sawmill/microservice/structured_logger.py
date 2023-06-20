"""Structured logger using gRPC."""

# khaleesi.ninja.
from khaleesi.core.logging.structured_logger import StructuredLogger
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest,
  GrpcResponseRequest,
  Error,
  Event,
  EmptyRequest,
  HttpRequest,
  HttpResponseRequest,
)
from microservice.models.service_registry import SERVICE_REGISTRY
from microservice.models import (
  GrpcRequest as DbGrpcRequest,
  Error as DbError,
  Event as DbEvent,
  HttpRequest as DbHttpRequest,
  Query as DbQuery,
)


class StructuredDbLogger(StructuredLogger):
  """Structured logger using gRPC."""

  def send_log_system_http_request(self, *, http_request: EmptyRequest) -> None:
    """Send the log request to the logging facility."""
    DbHttpRequest.objects.log_system_request(grpc_request = http_request)

  def send_log_http_request(self, *, http_request: HttpRequest) -> None:
    """Send the log request to the logging facility."""
    DbHttpRequest.objects.log_request(grpc_request = http_request)

  def send_log_http_response(self, *, http_response: HttpResponseRequest) -> None :
    """Send the log response to the logging facility."""
    DbHttpRequest.objects.log_response(grpc_response = http_response)

  def send_log_grpc_request(self, *, grpc_request: GrpcRequest) -> None :
    """Send the log request to the logging facility."""
    DbGrpcRequest.objects.log_request(grpc_request = grpc_request)
    SERVICE_REGISTRY.add_call(
      caller_details = grpc_request.upstreamRequest,
      called_details = grpc_request.requestMetadata.caller,
    )

  def send_log_grpc_response(self, *, grpc_response: GrpcResponseRequest) -> None :
    """Send the log response to the logging facility."""
    result = DbGrpcRequest.objects.log_response(grpc_response = grpc_response)
    # noinspection PyBroadException
    try:
      DbHttpRequest.objects.add_child_duration(request = result)
    except Exception:  # pylint: disable=broad-except
      # TODO(45) - remove this hack
      pass

    queries = DbQuery.objects.log_queries(
      queries = grpc_response.queries,
      metadata = result.to_grpc_request_response().request.requestMetadata,
    )
    for query in queries:
      result.meta_child_duration += query.reported_duration
    result.save()

  def send_log_error(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    DbError.objects.log_error(grpc_error = error)

  def send_log_event(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    DbEvent.objects.log_event(grpc_event = event)
