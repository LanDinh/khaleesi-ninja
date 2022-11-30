"""Exception test utility."""

# Python.
from functools import partial
from typing import Callable, Any

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException


def _raise(*args: Any, exception: Exception, method: Callable, **kwargs: Any) -> None :  # type: ignore[type-arg] # pylint: disable=line-too-long
  method(*args, **kwargs)
  raise exception

def default_khaleesi_exception(*, status: StatusCode) -> KhaleesiException :
  """Get a default instance of khaleesi exceptions."""
  return KhaleesiException(
    status          = status,
    gate            = 'gate',
    service         = 'service',
    public_key      = 'public-key',
    public_details  = 'public-details',
    private_message = 'private-message',
    private_details = 'private-details',
  )

def default_exception() -> Exception :
  """Get a default instance of exceptions."""
  return Exception("exception")

def khaleesi_raising_method(
    *,
    method: Callable = lambda *args, **kwargs: None,  # type: ignore[type-arg]
    status: StatusCode,
) -> Callable :  # type: ignore[type-arg]
  """Attach a khaleesi exception to a method."""
  exception = default_khaleesi_exception(status = status)
  return exception_raising_method(method = method, exception = exception)

def exception_raising_method(
    *,
    method: Callable = lambda *args, **kwargs: None,  # type: ignore[type-arg]
    exception: Exception = default_exception(),
) -> Callable :  # type: ignore[type-arg]
  """Attach an exception to a method."""
  return partial(
    lambda *args, inner_exception, inner_method, **kwargs:
    _raise(*args, exception = inner_exception, method = inner_method, **kwargs),
    inner_exception = exception,
    inner_method = method,
  )
