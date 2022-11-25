"""Interceptor to log incoming requests."""

# Python.
from datetime import timezone, datetime
from typing import Callable, Any

# Django.
from django.conf import settings

# gRPC.
from grpc import ServicerContext, StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
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
      **_: Any,
  ) -> Any :
    """Log the incoming request."""

    LOGGER.debug(message = f'{self._request_name()} request started (pre request_id)')
    self._log_request(request = request)
    LOGGER.info(message = f'{self._request_name()} request started')

    try:
      response = method(request, context)
      LOGGER.info(message = f'{self._request_name()} request finished successfully')
      self._log_response(status = StatusCode.OK)
      return response
    except KhaleesiException as exception:
      self._handle_exception(
        context      = context,
        exception    = exception,
      )
      raise
    except Exception as exception:
      new_exception = MaskingInternalServerException(exception = exception)
      self._handle_exception(
        context      = context,
        exception    = new_exception,
      )
      raise

  def _request_name(self) -> str :
    return f'{STATE.request.service_name}.{STATE.request.method_name}'

  def _handle_metadata(self, *, logging : Any, request : Any) -> None :
    """Handle the metadata for the request object."""
    if hasattr(request, 'request_metadata'):
      upstream = request.request_metadata
    else:
      upstream = RequestMetadata()

    add_request_metadata(
      request      = logging,
      request_id   = -1, # upstream request_id is in upstream part of the proto
      grpc_service = STATE.request.service_name,
      grpc_method  = STATE.request.method_name,
      user_id      = upstream.user.id,
      user_type    = upstream.user.type,
    )
    logging.upstream_request.request_id       = upstream.caller.request_id
    logging.upstream_request.khaleesi_gate    = upstream.caller.khaleesi_gate
    logging.upstream_request.khaleesi_service = upstream.caller.khaleesi_service
    logging.upstream_request.grpc_service     = upstream.caller.grpc_service
    logging.upstream_request.grpc_method      = upstream.caller.grpc_method

  def _log_request(self, *, request: Any) -> None :
    """Send the logging request to the logger."""

    logging_request = LoggingRequest()
    self._handle_metadata(logging = logging_request, request = request)

    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      response = self.stub.LogRequest(logging_request)
      STATE.request.id = response.request_id
    else:
      # Send directly to the DB. Note that Requests must be present in the schema!
      from microservice.models.service_registry import SERVICE_REGISTRY  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      from microservice.models import Request as DbRequest  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      logged_request = DbRequest.objects.log_request(grpc_request = logging_request)
      STATE.request.id = logged_request.pk
      SERVICE_REGISTRY.add_call(
        caller_details = logging_request.upstream_request,
        called_details = logging_request.request_metadata.caller,
      )

  def _log_response(self, status: StatusCode) -> None :
    """Send the logging response to the logger."""

    logging_response = LoggingResponse()
    logging_response.request_id = STATE.request.id
    logging_response.response.status = status.name
    logging_response.response.timestamp.FromDatetime(datetime.now(tz = timezone.utc))

    if khaleesi_settings['CORE']['STRUCTURED_LOGGING_METHOD'] == StructuredLoggingMethod.GRPC:
      self.stub.LogResponse(logging_response)
    else:
      # Send directly to the DB. Note that Requests must be present in the schema!
      from microservice.models import Request as DbRequest  # type: ignore[import,attr-defined]  # pylint: disable=import-error,import-outside-toplevel,no-name-in-module
      DbRequest.objects.log_response(grpc_response = logging_response)

  def _handle_exception(
      self, *,
      request   : Any,
      context   : ServicerContext,
  ) -> None :
    """Properly handle the exception."""
    LOGGER.error(message = f'{self._request_name()} request finished with errors')
    self._log_response(status = exception.status)
    context.set_code(exception.status)
    context.set_details(exception.to_json())
