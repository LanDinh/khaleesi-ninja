"""Custom exceptions."""

# Python.
import json
import traceback

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode


class KhaleesiException(Exception):
  """Base exception."""

  def __init__(
      self, *,
      status: StatusCode,
      gate: str,
      service: str,
      public_key: str,
      public_details: str,
      private_message: str,
      private_details: str,
  ) -> None :
    """Initialize the exception."""
    super().__init__(private_message)
    self.status          = status
    self.gate            = gate
    self.service         = service
    self.public_key      = public_key
    self.public_details  = public_details
    self.private_message = private_message
    self.private_details = private_details
    self.stacktrace      = ''.join(traceback.format_exception(None, self, self.__traceback__))

  def to_json(self) -> str :
    """Return a json string to encode this object."""
    result = {
        'status'         : self.status.name,
        'gate'           : self.gate,
        'service'        : self.service,
        'public_key'     : self.public_key,
        'public_details' : self.public_details,
    }
    if settings.DEBUG:
      result['private_message'] = self.private_message
      result['private_details'] = self.private_details
      result['stacktrace']      = self.stacktrace
    return json.dumps(result)


class KhaleesiCoreException(KhaleesiException):
  """Base core exception."""

  def __init__(
      self, *,
      status: StatusCode,
      public_key: str,
      public_details: str,
      private_message: str,
      private_details: str,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status = status,
      gate = 'core',
      service = 'core',
      public_key = public_key,
      public_details = public_details,
      private_message = private_message,
      private_details = private_details,
    )


class InvalidArgumentException(KhaleesiCoreException):
  """Invalid arguments."""

  def __init__(
      self, *,
      public_details: str = '',
      private_message: str,
      private_details: str,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status = StatusCode.INVALID_ARGUMENT,
      public_key = 'invalid-argument',
      public_details = public_details,
      private_message = private_message,
      private_details = private_details,
    )


class InternalServerException(KhaleesiCoreException):
  """Internal server errors."""

  def __init__(self, *, private_message: str, private_details: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status = StatusCode.INTERNAL,
      public_key = 'internal-server-error',
      public_details = '',
      private_message = private_message,
      private_details = private_details,
    )

class MaskingInternalServerException(InternalServerException):
  """Mask other exceptions as internal server error."""

  def __init__(self, *, exception: Exception) -> None :
    """Initialize the exception."""
    super().__init__(
      private_message = type(exception).__name__,
      private_details = str(exception),
    )
    self.__traceback__ = exception.__traceback__


class ProgrammingException(InternalServerException):
  """Programming errors."""


class UpstreamGrpcException(KhaleesiCoreException):
  """Internal server errors."""

  def __init__(self, *, status: StatusCode, private_details: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status = status,
      public_key = 'upstream-grpc-error',
      public_details = '',
      private_message = f'Upstream error {status} received.',
      private_details = private_details,
    )
