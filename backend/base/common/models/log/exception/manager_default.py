"""Default Manager."""

# Python.
import traceback

# khaleesi.ninja.
from common.exceptions import KhaleesiException
from common.models.log.request.model import LogRequest
from common.models.manager import  Manager, T


class DefaultManager(Manager[T]):
  """Default Manager."""

  # noinspection PyUnresolvedReferences,PyTypeHints,PyMissingOrEmptyDocstring
  def create_khaleesi(self, *, request: LogRequest, exception: KhaleesiException) -> None :
    """Create a new exception log."""
    log = self._create(request = request, exception = exception)
    log.http_code = exception.code  # type: ignore[attr-defined]
    log.data = str(exception.data)  # type: ignore[attr-defined]
    log.save()

  def create_extern(self, *, request: LogRequest, exception: Exception) -> None :
    """Create a new exception log."""
    log = self._create(request = request, exception = exception)
    log.save()

  def _create(self, *, request: LogRequest, exception: Exception) -> T :
    tb_exception = traceback.TracebackException.from_exception(exception)
    log = self.model(
        request = request,
        exception = tb_exception.exc_type.__name__,
        message = str(exception),
        stacktrace = tb_exception.format(),
    )
    return log
