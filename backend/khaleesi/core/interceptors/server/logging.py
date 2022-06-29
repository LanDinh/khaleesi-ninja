"""Interceptor to log incoming requests."""

# Python.
from datetime import timezone, datetime
from typing import Callable, Any

# Django.
from django.conf import settings

# gRPC.
from grpc import ServicerContext
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.grpc.channels import ChannelManager
from khaleesi.core.grpc.request_metadata import add_request_metadata
from khaleesi.core.interceptors.server.util import ServerInterceptor
from khaleesi.core.settings.definition import KhaleesiNinjaSettings, StructuredLoggingMethod
from khaleesi.core.shared.logger import LOGGER
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import (
  Request as LoggingRequest,
  ResponseRequest as LoggingResponse,
)
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

    LOGGER.debug(message = f'{service_name}.{method_name} request started (pre request_id)')
    self._log_request(request = request, service_name = service_name, method_name = method_name)
    LOGGER.info(message = f'{service_name}.{method_name} request started')

    response = None
    try:
      response = method(request, context)
      self._log_response(status = StatusCode.OK)
      LOGGER.info(
        message = f'{service_name}.{method_name} request finished successfully',
      )
    except KhaleesiException as exception:
      self._log_response(status = exception.status)
      LOGGER.error(
        message = f'{service_name}.{method_name} request finished with errors',
      )

    del STATE.request_id
    return response

  def _log_request(
      self, *,
      request: Any,
      service_name: str,
      method_name: str,
  ) -> None :
    """Send the logging request to the logger."""

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

    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      response = self.stub.LogRequest(logging_request)
      STATE.request_id = response.request_id
    else:
      # Send directly to the DB. Note that Requests must be present in the schema!
      from microservice.models import Request as DbRequest  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      logged_request = DbRequest.objects.log_request(grpc_request = logging_request)
      STATE.request_id = logged_request.pk

  def _log_response(self, status: StatusCode) -> None :
    """Send the logging response to the logger."""

    logging_response = LoggingResponse()
    logging_response.request_id = STATE.request_id
    logging_response.response.status = status.name
    logging_response.response.timestamp.FromDatetime(datetime.now(tz = timezone.utc))

    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      self.stub.LogResponse(logging_response)
    else:
      # Send directly to the DB. Note that Requests must be present in the schema!
      from microservice.models import Request as DbRequest  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      DbRequest.objects.log_response(grpc_response = logging_response)
