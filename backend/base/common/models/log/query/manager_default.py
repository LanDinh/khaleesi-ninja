"""Default Manager."""

# Python.
from datetime import timedelta
# noinspection SyntaxError,PyMissingOrEmptyDocstring,PyUnresolvedReferences
import sql_metadata  # type: ignore[import]

# khaleesi.ninja.
from common.models.log.request.model import LogRequest
from common.models.manager import  Manager, T


class DefaultManager(Manager[T]):
  """Default Manager."""

  # noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
  def create(  # type: ignore[override]
      self, *,
      request: LogRequest,
      nanoseconds: int,
      sql: str,
  ) -> None :
    """Create a new query log."""
    tables = sql_metadata.get_query_tables(sql)
    log = self.model(
        request = request,
        time = timedelta(microseconds = nanoseconds//1000),
        operation = sql.split(maxsplit = 1)[0],
        main_table = tables[0] if len(tables) > 0 else None,
        join_table = ', '.join(tables[1:]) if len(tables) > 1 else None,
        sql = sql,
    )
    log.save()
