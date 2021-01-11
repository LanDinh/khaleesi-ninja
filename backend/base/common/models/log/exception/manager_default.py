"""Default Manager."""

# Python.
import traceback

# khaleesi.ninja.
from common.exceptions import KhaleesiException
from common.models.manager import  Manager, T


class DefaultManager(Manager[T]):
  """Default Manager."""

  # noinspection PyUnresolvedReferences,PyTypeHints,PyMissingOrEmptyDocstring
  def create_khaleesi(self, *, exception: KhaleesiException) -> None :
    """Create a new exception log."""
    log = self._create(exception = exception)
    log.http_code = exception.code  # type: ignore[attr-defined]
    log.data = str(exception.data)  # type: ignore[attr-defined]
    log.save()

  def create_extern(self, *, exception: Exception) -> None :
    """Create a new exception log."""
    log = self._create(exception = exception)
    log.save()

  def _create(self, *, exception: Exception) -> T :
    tb_exception = traceback.TracebackException.from_exception(exception)
    log = self.model(
        exception = tb_exception.exc_type.__name__,
        message = str(exception),
        stacktrace = tb_exception.format(),
    )
    return log
