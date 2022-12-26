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
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import (
  Request,
  ResponseRequest,
  Error,
  Event,
  EmptyRequest,
  BackgateRequest,
)
from khaleesi.proto.core_sawmill_pb2_grpc import LumberjackStub


khaleesi_settings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class StructuredLogger(ABC):
  """Basic structured logger."""

  # noinspection PyUnusedLocal
  def __init__(self, *, channel_manager: ChannelManager) -> None :
    """Initialization."""

  def log_request(self, *, upstream_request: RequestMetadata) -> None :
    """Log a microservice request."""
    LOGGER.info(
      f'User "{STATE.user.user_id}" started request '
      f'{STATE.request.grpc_service}.{STATE.request.grpc_method}.'
    )
    LOGGER.info(f'Upstream request "{upstream_request.caller.request_id}" caller data: '
      f'{upstream_request.caller.khaleesi_gate}-{upstream_request.caller.khaleesi_service}: '
      f'{upstream_request.caller.grpc_service}.{upstream_request.caller.grpc_method}'
    )

    request = Request()
    add_request_metadata(request = request)
    request.upstream_request.request_id       = upstream_request.caller.request_id
    request.upstream_request.khaleesi_gate    = upstream_request.caller.khaleesi_gate
    request.upstream_request.khaleesi_service = upstream_request.caller.khaleesi_service
    request.upstream_request.grpc_service     = upstream_request.caller.grpc_service
    request.upstream_request.grpc_method      = upstream_request.caller.grpc_method

    self.send_log_request(request = request)

  def log_response(self, *, status: StatusCode) -> None :
    """Log a microservice response."""
    response = self._log_response_object(
      status = status,
      request_id = STATE.request.request_id,
      request_name = 'Request',
    )
    self.send_log_response(response = response)

  def log_error(self, *, exception: KhaleesiException ) -> None :
    """Log an exception."""
    LOGGER.log(exception.to_json(), loglevel = exception.loglevel)
    LOGGER.log(exception.stacktrace, loglevel = exception.loglevel)

    error = Error()
    add_request_metadata(request = error)
    error.status          = exception.status.name
    error.loglevel        = exception.loglevel.name
    error.gate            = exception.gate
    error.service         = exception.service
    error.public_key      = exception.public_key
    error.public_details  = exception.public_details
    error.private_message = exception.private_message
    error.private_details = exception.private_details
    error.stacktrace      = exception.stacktrace

    self.send_log_error(error = error)

  def log_system_backgate_request(self, *, backgate_request_id: str, grpc_method: str) -> None :
    """Log a backgate request for system requests."""
    LOGGER.info(
      f'Backgate request "{backgate_request_id}" started.'
    )
    backgate_request = EmptyRequest()
    add_grpc_server_system_request_metadata(
      request             = backgate_request,
      grpc_method         = grpc_method,
      backgate_request_id = backgate_request_id,
    )
    self.send_log_system_backgate_request(backgate_request = backgate_request)

  def log_backgate_request(self) -> None :
    """Log a backgate request for system requests."""
    LOGGER.info(
      f'Backgate request "{STATE.request.backgate_request_id}" started.'
    )
    backgate_request = BackgateRequest()
    add_request_metadata(request = backgate_request)
    self.send_log_backgate_request(backgate_request = backgate_request)


  def log_backgate_response(
      self, *,
      status: StatusCode,
      backgate_request_id: str = STATE.request.backgate_request_id,
  ) -> None :
    """Log a microservice backgate response."""
    response = self._log_response_object(
      status = status,
      request_id = backgate_request_id,
      request_name = f'Backgate request "{backgate_request_id}"',
    )
    self.send_log_backgate_response(response = response)

  def log_system_event(
      self, *,
      backgate_request_id: str,
      grpc_method        : str,
      target             : str,
      owner              : User,
      action             : 'Event.Action.ActionType.V',
      result             : 'Event.Action.ResultType.V',
      details            : str,
      logger_send_metric : bool,
  ) -> None :
    """Log an event."""
    target_type = khaleesi_settings['GRPC']['SERVER_METHOD_NAMES'][grpc_method]['TARGET']  # type: ignore[literal-required]  # pylint: disable=line-too-long
    log_string = \
      f'Event targeting "{target_type}": "{target}" owned by "{owner.id}". '\
      f'{Event.Action.ActionType.Name(action)} with result {Event.Action.ResultType.Name(result)}.'

    if result == Event.Action.ResultType.SUCCESS:
      LOGGER.info(log_string)
    elif result == Event.Action.ResultType.WARNING:
      LOGGER.warning(log_string)
    elif result == Event.Action.ResultType.ERROR:
      LOGGER.error(log_string)
    elif result == Event.Action.ResultType.FATAL:
      LOGGER.fatal(log_string)
    else:
      LOGGER.fatal(log_string)

    event = Event()
    add_grpc_server_system_request_metadata(
      request             = event,
      grpc_method         = grpc_method,
      backgate_request_id = backgate_request_id,
    )
    # noinspection PyTypedDict
    event.target.type        = target_type
    event.target.id          = target
    event.target.owner.id    = owner.id
    event.target.owner.type  = owner.type
    event.action.crud_type   = action
    event.action.result      = result
    event.action.details     = details
    event.logger_send_metric = logger_send_metric

    self.send_log_event(event = event)

  def _log_response_object(
      self, *,
      status: StatusCode,
      request_id: str,
      request_name: str,
  ) -> ResponseRequest :
    """Text log a response and return the response object."""
    if status == StatusCode.OK:
      LOGGER.info(f'{request_name} finished successfully.')
    else:
      LOGGER.warning(f'{request_name} finished with error code {status.name}.')

    response                 = ResponseRequest()
    response.request_id      = request_id
    response.response.status = status.name
    response.response.timestamp.FromDatetime(datetime.now(tz = timezone.utc))

    return response

  @abstractmethod
  def send_log_system_backgate_request(self, *, backgate_request: EmptyRequest) -> None :
    """Send the backgate log request to the logging facility."""

  @abstractmethod
  def send_log_backgate_request(self, *, backgate_request: BackgateRequest) -> None :
    """Send the backgate log request to the logging facility."""

  @abstractmethod
  def send_log_backgate_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""

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

  def send_log_system_backgate_request(self, *, backgate_request: EmptyRequest) -> None:
    """Send the log request to the logging facility."""
    self.stub.LogSystemBackgateRequest(backgate_request)

  def send_log_backgate_request(self, *, backgate_request: BackgateRequest) -> None:
    """Send the log request to the logging facility."""
    self.stub.LogBackgateRequest(backgate_request)

  def send_log_backgate_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    self.stub.LogBackgateRequestResponse(response)

  def send_log_request(self, *, request: Request) -> None :
    """Send the log request to the logging facility."""
    self.stub.LogRequest(request)

  def send_log_response(self, *, response: ResponseRequest) -> None :
    """Send the log response to the logging facility."""
    self.stub.LogResponse(response)

  def send_log_error(self, *, error: Error) -> None :
    """Send the log error to the logging facility."""
    self.stub.LogError(error)

  def send_log_event(self, *, event: Event) -> None :
    """Send the log event to the logging facility."""
    self.stub.LogEvent(event)
