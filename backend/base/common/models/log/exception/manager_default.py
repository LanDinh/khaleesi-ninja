"""Default Manager."""

# Python.
import traceback

# khaleesi.ninja.
from common.exceptions import KhaleesiException
from common.models.manager import  Manager


class DefaultManager(Manager):
  """Default Manager."""

  def create(self, *, exception: Exception) -> None :
    """Create a new exception log."""
    tb_exception = traceback.TracebackException.from_exception(exception)
    log = self.model(
        exception = tb_exception.exc_type.__name__,
        message = str(exception),
        stacktrace = tb_exception.format(),
    )
    if isinstance(exception, KhaleesiException):
      log.http_code = exception.code
      log.data = str(exception.data)
    log.save()
