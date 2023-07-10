"""Custom exceptions."""

# Python.
from json import dumps
from traceback import format_exception

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.proto.core_pb2 import ObjectMetadata


class KhaleesiException(Exception):
  """Base exception."""

  def __init__(
      self, *,
      status        : StatusCode,
      gate          : str,
      service       : str,
      publicKey     : str,
      publicDetails : str,
      privateMessage: str,
      privateDetails: str,
      loglevel      : LogLevel,
  ) -> None :
    """Initialize the exception."""
    super().__init__(privateMessage)
    self.status         = status
    self.gate           = gate
    self.service        = service
    self.publicKey      = publicKey
    self.publicDetails  = publicDetails
    self.privateMessage = privateMessage
    self.privateDetails = privateDetails
    self.loglevel       = loglevel

  @property
  def stacktrace(self) -> str :
    """Return the stacktrace of the exception."""
    return ''.join(format_exception(None, self, self.__traceback__))

  def toJson(self) -> str :
    """Return a json string to encode this object."""
    result = {
        'status'        : self.status.name,
        'gate'          : self.gate,
        'service'       : self.service,
        'publicKey'     : self.publicKey,
        'publicDetails' : self.publicDetails,
    }
    if settings.DEBUG:
      result['privateMessage'] = self.privateMessage
      result['privateDetails'] = self.privateDetails
      result['stacktrace']     = self.stacktrace
    return dumps(result)


class KhaleesiCoreException(KhaleesiException):
  """Base core exception."""

  def __init__(
      self, *,
      status        : StatusCode,
      publicKey     : str,
      publicDetails : str,
      privateMessage: str,
      privateDetails: str,
      loglevel      : LogLevel,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = status,
      gate           = 'core',
      service        = 'core',
      publicKey      = publicKey,
      publicDetails  = publicDetails,
      privateMessage = privateMessage,
      privateDetails = privateDetails,
      loglevel       = loglevel,
    )


class InvalidArgumentException(KhaleesiCoreException):
  """Invalid arguments."""

  def __init__(
      self, *,
      publicDetails : str = '',
      privateMessage: str,
      privateDetails: str,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = StatusCode.INVALID_ARGUMENT,
      publicKey      = 'core-invalid-argument',
      publicDetails  = publicDetails,
      privateMessage = privateMessage,
      privateDetails = privateDetails,
      loglevel       = LogLevel.WARNING,
    )


class InternalServerException(KhaleesiCoreException):
  """Internal server errors."""

  def __init__(self, *, privateMessage: str, privateDetails: str, loglevel: LogLevel) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = StatusCode.INTERNAL,
      publicKey      = 'core-internal-server-error',
      publicDetails  = '',
      privateMessage = privateMessage,
      privateDetails = privateDetails,
      loglevel       = loglevel,
    )

class MaskingInternalServerException(InternalServerException):
  """Mask other exceptions as internal server error."""

  def __init__(self, *, exception: Exception) -> None :
    """Initialize the exception."""
    super().__init__(
      privateMessage = type(exception).__name__,
      privateDetails = str(exception),
      loglevel       = LogLevel.FATAL,
    )
    self.__traceback__ = exception.__traceback__


class ProgrammingException(InternalServerException):
  """Programming errors."""

  def __init__(self, *, privateMessage: str, privateDetails: str) -> None :
    """Initialize the exception."""
    super().__init__(
      privateMessage = privateMessage,
      privateDetails = privateDetails,
      loglevel       = LogLevel.FATAL,
    )


class UpstreamGrpcException(KhaleesiCoreException):
  """Error in upstream gRPC request."""

  def __init__(self, *, status: StatusCode, privateDetails: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = status,
      publicKey      = 'core-upstream-grpc-error',
      publicDetails  = '',
      privateMessage = f'Upstream error {status} received.',
      privateDetails = privateDetails,
      loglevel       = LogLevel.ERROR
    )


class TimeoutException(KhaleesiCoreException):
  """Timeouts."""

  def __init__(self, *, privateDetails: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = StatusCode.DEADLINE_EXCEEDED,
      publicKey      = 'core-timeout-error',
      publicDetails  = '',
      privateMessage = 'Timeout happened.',
      privateDetails = privateDetails,
      loglevel       = LogLevel.ERROR,
    )


class DbException(KhaleesiCoreException):
  """DB-related exceptions."""


class DbOutdatedInformationException(DbException):
  """Django MultipleObjectsReturned."""

  def __init__(self, *, objectType: str, metadata: ObjectMetadata) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = StatusCode.FAILED_PRECONDITION,
      publicKey      = 'core-db-outdated-information',
      publicDetails  = '',
      privateMessage = f'{objectType} has been changed in the meantime.',
      privateDetails = f'objectType: {objectType}, id: {metadata.id}',
      loglevel       = LogLevel.ERROR,
    )

class DbObjectNotFoundException(DbException):
  """Django ObjectDoesNotExist."""

  def __init__(
      self, *,
      objectType: str,
      loglevel   : LogLevel = LogLevel.WARNING,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = StatusCode.NOT_FOUND,
      publicKey      = 'core-db-object-not-found',
      publicDetails  = objectType,
      privateMessage = f'{objectType} not found in the DB.',
      privateDetails = objectType,
      loglevel       = loglevel,
    )


class DbObjectTwinException(DbException):
  """Django MultipleObjectsReturned."""

  def __init__(
      self, *,
      objectType: str,
      objectId  : str,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status         = StatusCode.FAILED_PRECONDITION,
      publicKey      = 'core-db-object-twin',
      publicDetails  = objectType,
      privateMessage = f'{objectType} found multiple times in the DB.',
      privateDetails = f'objectType: {objectType}, objectId: {objectId}',
      loglevel       = LogLevel.ERROR,
    )


