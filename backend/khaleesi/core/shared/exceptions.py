"""Custom exceptions."""

# Python.
from json import dumps
from traceback import format_exception

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LogLevel


class KhaleesiException(Exception):
  """Base exception."""

  def __init__(
      self, *,
      status         : StatusCode,
      gate           : str,
      service        : str,
      public_key     : str,
      public_details : str,
      private_message: str,
      private_details: str,
      loglevel       : LogLevel,
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
    self.loglevel        = loglevel

  @property
  def stacktrace(self) -> str :
    """Return the stacktrace of the exception."""
    return ''.join(format_exception(None, self, self.__traceback__))

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
    return dumps(result)


class KhaleesiCoreException(KhaleesiException):
  """Base core exception."""

  def __init__(
      self, *,
      status         : StatusCode,
      public_key     : str,
      public_details : str,
      private_message: str,
      private_details: str,
      loglevel       : LogLevel,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status          = status,
      gate            = 'core',
      service         = 'core',
      public_key      = public_key,
      public_details  = public_details,
      private_message = private_message,
      private_details = private_details,
      loglevel        = loglevel,
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
      status          = StatusCode.INVALID_ARGUMENT,
      public_key      = 'core-invalid-argument',
      public_details  = public_details,
      private_message = private_message,
      private_details = private_details,
      loglevel        = LogLevel.WARNING,
    )


class InternalServerException(KhaleesiCoreException):
  """Internal server errors."""

  def __init__(self, *, private_message: str, private_details: str, loglevel: LogLevel) -> None :
    """Initialize the exception."""
    super().__init__(
      status          = StatusCode.INTERNAL,
      public_key      = 'core-internal-server-error',
      public_details  = '',
      private_message = private_message,
      private_details = private_details,
      loglevel        = loglevel,
    )

class MaskingInternalServerException(InternalServerException):
  """Mask other exceptions as internal server error."""

  def __init__(self, *, exception: Exception) -> None :
    """Initialize the exception."""
    super().__init__(
      private_message = type(exception).__name__,
      private_details = str(exception),
      loglevel        = LogLevel.FATAL,
    )
    self.__traceback__ = exception.__traceback__


class ProgrammingException(InternalServerException):
  """Programming errors."""

  def __init__(self, *, private_message: str, private_details: str) -> None :
    """Initialize the exception."""
    super().__init__(
      private_message = private_message,
      private_details = private_details,
      loglevel        = LogLevel.FATAL,
    )


class UpstreamGrpcException(KhaleesiCoreException):
  """Error in upstream gRPC request."""

  def __init__(self, *, status: StatusCode, private_details: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status          = status,
      public_key      = 'core-upstream-grpc-error',
      public_details  = '',
      private_message = f'Upstream error {status} received.',
      private_details = private_details,
      loglevel        = LogLevel.ERROR
    )


class TimeoutException(KhaleesiCoreException):
  """Timeouts."""

  def __init__(self, *, private_details: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status          = StatusCode.DEADLINE_EXCEEDED,
      public_key      = 'core-timeout-error',
      public_details  = '',
      private_message = 'Timeout happened.',
      private_details = private_details,
      loglevel        = LogLevel.ERROR,
    )


class DbException(KhaleesiCoreException):
  """DB-related exceptions."""


class DbObjectNotFoundException(DbException):
  """Django ObjectDoesNotExist."""

  def __init__(
      self, *,
      object_type: str,
      loglevel   : LogLevel = LogLevel.WARNING,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status          = StatusCode.NOT_FOUND,
      public_key      = 'core-db-object-not-found',
      public_details  = object_type,
      private_message = f'{object_type} not found in the DB.',
      private_details = object_type,
      loglevel        = loglevel,
    )


class DbObjectTwinException(DbException):
  """Django MultipleObjectsReturned."""

  def __init__(
      self, *,
      object_type: str,
      object_id  : str,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status          = StatusCode.FAILED_PRECONDITION,
      public_key      = 'core-db-object-twin',
      public_details  = object_type,
      private_message = f'{object_type} found multiple times in the DB.',
      private_details = f'object_type: {object_type}, object_id: {object_id}',
      loglevel        = LogLevel.ERROR,
    )
