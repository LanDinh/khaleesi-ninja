"""Default Manager."""

# Python.
from datetime import timedelta
from typing import Optional

# khaleesi.ninja.
from common.models.log.request.model import LogRequest
from common.models.manager import  Manager, T


class DefaultManager(Manager[T]):
  """Default Manager."""

  # noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
  def create(  # type: ignore[override]
      self, *,
      request: LogRequest,
      time: int,  # microseconds.
      operation: str,
      main_table: str,
      join_table: Optional[str],
      sql: str,
  ) -> None :
    """Create a new query log."""
    log = self.model(
        request = request,
        time = timedelta(microseconds = time),
        operation = operation,
        main_table = main_table,
        join_table = join_table,
        sql = sql,
    )
    log.save()
