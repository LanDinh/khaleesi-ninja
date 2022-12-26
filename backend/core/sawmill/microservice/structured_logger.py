"""Structured logger using gRPC."""

# khaleesi.ninja.
from khaleesi.core.shared.structured_logger import StructuredLogger
from khaleesi.proto.core_sawmill_pb2 import (
  Request,
  ResponseRequest,
  Error,
  Event,
  EmptyRequest,
  BackgateRequest,
)
from microservice.models.service_registry import SERVICE_REGISTRY
from microservice.models import (
  Request as DbRequest,
  Error as DbError,
  Event as DbEvent,
  BackgateRequest as DbBackgateRequest,
)


class StructuredDbLogger(StructuredLogger):
  """Structured logger using gRPC."""

  def send_log_system_backgate_request(self, *, backgate_request: EmptyRequest) -> None:
    """Send the log request to the logging facility."""
    DbBackgateRequest.objects.log_system_backgate_request(grpc_backgate_request = backgate_request)

  def send_log_backgate_request(self, *, backgate_request: BackgateRequest) -> None:
    """Send the log request to the logging facility."""
    DbBackgateRequest.objects.log_backgate_request(grpc_backgate_request = backgate_request)

  def send_log_backgate_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    DbBackgateRequest.objects.log_response(grpc_response = response)

  def send_log_request(self, *, request: Request) -> None :
    """Send the log request to the logging facility."""
    DbRequest.objects.log_request(grpc_request = request)
    SERVICE_REGISTRY.add_call(
      caller_details = request.upstream_request,
      called_details = request.request_metadata.caller,
    )

  def send_log_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    DbRequest.objects.log_response(grpc_response = response)

  def send_log_error(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    DbError.objects.log_error(grpc_error = error)

  def send_log_event(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    DbEvent.objects.log_event(grpc_event = event)
