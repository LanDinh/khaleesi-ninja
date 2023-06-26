"""Exception test utility."""

# Python.
from functools import partial
from typing import Callable, Any

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.logging.textLogger import LogLevel


def _raise(*args: Any, exception: Exception, method: Callable, **kwargs: Any) -> None :  # type: ignore[type-arg] # pylint: disable=line-too-long
  method(*args, **kwargs)
  raise exception

def defaultKhaleesiException(*, status: StatusCode, loglevel: LogLevel) -> KhaleesiException :
  """Get a default instance of khaleesi exceptions."""
  return KhaleesiException(
    status         = status,
    loglevel       = loglevel,
    gate           = 'gate',
    service        = 'service',
    publicKey      = 'public-key',
    publicDetails  = 'public-details',
    privateMessage = 'private-message',
    privateDetails = 'private-details',
  )

def defaultException() -> Exception :
  """Get a default instance of exceptions."""
  return Exception("exception")

def khaleesiRaisingMethod(
    *,
    method  : Callable = lambda *args, **kwargs: None,  # type: ignore[type-arg]
    status  : StatusCode,
    loglevel: LogLevel,
) -> Callable :  # type: ignore[type-arg]
  """Attach a khaleesi exception to a method."""
  exception = defaultKhaleesiException(status = status, loglevel = loglevel)
  return exceptionRaisingMethod(method = method, exception = exception)

def exceptionRaisingMethod(
    *,
    method   : Callable = lambda *args, **kwargs: None,  # type: ignore[type-arg]
    exception: Exception = defaultException(),
) -> Callable :  # type: ignore[type-arg]
  """Attach an exception to a method."""
  return partial(
    lambda *args, innerException, innerMethod, **kwargs:
    _raise(*args, exception = innerException, method = innerMethod, **kwargs),
    innerException = exception,
    innerMethod    = method,
  )
