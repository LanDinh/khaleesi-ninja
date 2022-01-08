"""core-sawmill service."""

# Python.
from typing import Callable

# gRPC.
import grpc

# khaleesi-ninja.
from khaleesi.core.service_configuration import ServiceConfiguration
from khaleesi.proto.core_sawmill_pb2 import DESCRIPTOR, Event, LogResponse
from khaleesi.proto.core_sawmill_pb2_grpc import (
    LumberjackServicer as Servicer,
    add_LumberjackServicer_to_server as add_to_server
)
from microservice.models import Event as DbEvent
from microservice.models.abstract import Metadata


class Service(Servicer):
  """core-sawmill service."""

  def LogEvent(self, request: Event, context: grpc.ServicerContext) -> LogResponse :
    """Log events."""
    return self._handle_response(
      method = lambda: DbEvent.objects.log_event(grpc_event = request),
      context = context,
    )

  @staticmethod
  def _handle_response(
      *,
      method: Callable[[], Metadata],
      context: grpc.ServicerContext,
  ) -> LogResponse :
    """Wrap responses for logging."""
    response = LogResponse()
    try:
      metadata = method()
      if metadata.meta_logging_errors:
        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
        context.set_details(metadata.meta_logging_errors)
    except Exception as exception:  # pylint: disable=broad-except
      context.set_code(grpc.StatusCode.INTERNAL)
      context.set_details(f'{type(exception).__name__}: {str(exception)}')
    return response


service_configuration = ServiceConfiguration[Service](
  name = DESCRIPTOR.services_by_name['Lumberjack'].full_name,
  add_service_to_server = add_to_server,
  service = Service()
)
