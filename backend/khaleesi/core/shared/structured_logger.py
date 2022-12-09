"""Basic structured logger."""

# Python.
from abc import ABC, abstractmethod
from datetime import timezone, datetime

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.grpc.channels import ChannelManager
from khaleesi.core.grpc.request_metadata import (
  add_request_metadata,
  add_grpc_server_system_request_metadata,
)
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.shared.logger import LOGGER
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import Request, ResponseRequest, Error, Event
from khaleesi.proto.core_sawmill_pb2_grpc import LumberjackStub


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class StructuredLogger(ABC):
  """Basic structured logger."""

  def __init__(self, *, channel_manager: ChannelManager) -> None :
    """Initialization."""

  def log_request(self, *, upstream_request: RequestMetadata) -> None :
    """Log a microservice request."""
    request = Request()
    add_request_metadata(request = request)
    request.upstream_request.request_id       = upstream_request.caller.request_id
    request.upstream_request.khaleesi_gate    = upstream_request.caller.khaleesi_gate
    request.upstream_request.khaleesi_service = upstream_request.caller.khaleesi_service
    request.upstream_request.grpc_service     = upstream_request.caller.grpc_service
    request.upstream_request.grpc_method      = upstream_request.caller.grpc_method
    self.send_log_request(request = request)
    LOGGER.info(f'{STATE.request.grpc_service}.{STATE.request.grpc_method} request started')

  def log_response(self, status: StatusCode) -> None :
    """Log a microservice response."""
    if status == StatusCode.OK:
      LOGGER.info(
        f'{STATE.request.grpc_service}.{STATE.request.grpc_method}'
        ' request finished successfully'
      )
    else:
      LOGGER.warning(
        f'{STATE.request.grpc_service}.{STATE.request.grpc_method}'
        ' request finished with errors'
      )
    response = ResponseRequest()
    response.request_id = STATE.request.id
    response.response.status = status.name
    response.response.timestamp.FromDatetime(datetime.now(tz = timezone.utc))
    self.send_log_response(response = response)

  def log_error(self, *, exception: KhaleesiException ) -> None :
    """Log an exception."""
    error = Error()
    add_request_metadata(request = error)
    error.status          = exception.status.name
    error.gate            = exception.gate
    error.service         = exception.service
    error.public_key      = exception.public_key
    error.public_details  = exception.public_details
    error.private_message = exception.private_message
    error.private_details = exception.private_details
    error.stacktrace      = exception.stacktrace
    self.send_log_error(error = error)

  def log_system_event(
      self, *,
      grpc_method: str,
      action: 'Event.Action.ActionType.V',
      result: 'Event.Action.ResultType.V',
      details: str,
  ) -> None :
    """Log an event."""
    if result == Event.Action.ResultType.SUCCESS:
      LOGGER.info(details)
    elif result == Event.Action.ResultType.WARNING:
      LOGGER.warning(details)
    elif result == Event.Action.ResultType.ERROR:
      LOGGER.error(details)
    elif result == Event.Action.ResultType.FATAL:
      LOGGER.fatal(details)
    else:
      LOGGER.fatal(details)
    event = Event()
    add_grpc_server_system_request_metadata(request = event, grpc_method = grpc_method)
    event.target.type = khaleesi_settings['GRPC']['SERVER_METHOD_NAMES'][grpc_method]['TARGET']  # type: ignore[literal-required]  # pylint: disable=line-too-long
    event.action.crud_type = action
    event.action.result    = result
    event.action.details   = details
    self.send_log_event(event = event)

  @abstractmethod
  def send_log_request(self, *, request: Request) -> None :
    """Send the log request to the logging facility."""

  @abstractmethod
  def send_log_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""

  @abstractmethod
  def send_log_error(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""

  @abstractmethod
  def send_log_event(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""


class StructuredGrpcLogger(StructuredLogger):
  """Structured logger using gRPC."""

  stub: LumberjackStub

  def __init__(self, *, channel_manager: ChannelManager) -> None :
    super().__init__(channel_manager = channel_manager)
    channel = channel_manager.get_channel(gate = 'core', service = 'sawmill')
    self.stub = LumberjackStub(channel)  # type: ignore[no-untyped-call]

  def send_log_request(self, *, request: Request) -> None :
    """Send the log request to the logging facility."""
    response = self.stub.LogRequest(request)
    STATE.request.id = response.request_id

  def send_log_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    self.stub.LogResponse(response)

  def send_log_error(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    self.stub.LogError(error)

  def send_log_event(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    self.stub.LogEvent(event)
