"""Interceptor to log incoming requests."""

# Python.
from typing import Callable, Any

# Django.
from django.conf import settings

# gRPC.
from grpc import ServicerContext

# khaleesi.ninja.
from khaleesi.core.grpc.channels import ChannelManager
from khaleesi.core.grpc.request_metadata import add_request_metadata
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.settings.definition import KhaleesiNinjaSettings, StructuredLoggingMethod
from khaleesi.core.shared.logger import LOGGER
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import Request as LoggingRequest
from khaleesi.proto.core_sawmill_pb2_grpc import LumberjackStub


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


class LoggingServerInterceptor(ServerInterceptor):
  """Interceptor to log requests."""

  stub: LumberjackStub

  def __init__(self, *, channel_manager: ChannelManager) -> None :
    super().__init__()
    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      channel = channel_manager.get_channel(gate = 'core', service = 'sawmill')
      self.stub = LumberjackStub(channel)  # type: ignore[no-untyped-call]

  def khaleesi_intercept(
      self, *,
      method: Callable[[Any, ServicerContext], Any],
      request: Any,
      context: ServicerContext,
      service_name: str,
      method_name: str,
  ) -> Any :
    """Log the incoming request."""
    if hasattr(request, 'request_metadata'):
      upstream: RequestMetadata = request.request_metadata
    else:
      upstream = RequestMetadata()

    logging_request = LoggingRequest()
    add_request_metadata(
      request      = logging_request,
      request_id   = -1, # upstream request_id is in upstream part of the proto
      grpc_service = service_name,
      grpc_method  = method_name,
      user_id      = upstream.user.id,
      user_type    = upstream.user.type,
    )
    logging_request.upstream_request.request_id       = upstream.caller.request_id
    logging_request.upstream_request.khaleesi_gate    = upstream.caller.khaleesi_gate
    logging_request.upstream_request.khaleesi_service = upstream.caller.khaleesi_service
    logging_request.upstream_request.grpc_service     = upstream.caller.grpc_service
    logging_request.upstream_request.grpc_method      = upstream.caller.grpc_method

    LOGGER.debug(message = f'{service_name}.{method_name} request started (pre request_id)')

    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      response = self.stub.LogRequest(logging_request)
      STATE.request_id = response.request_id
    else:
      # Send directly to the DB. Note that Requests must be present in the schema!
      from microservice.models import Request as DbRequest  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      logged_request = DbRequest.objects.log_request(grpc_request = logging_request)
      STATE.request_id = logged_request.pk

    LOGGER.info(message = f'{service_name}.{method_name} request started')

    response = method(request, context)
    return response
