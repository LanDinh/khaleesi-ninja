"""Custom database backend. THE FILE NAME IS ESSENTIAL!"""

# Python.
import time
from contextlib import contextmanager
from typing import Any, Optional, Sized
# noinspection SyntaxError,PyMissingOrEmptyDocstring,PyUnresolvedReferences
import sql_metadata  # type: ignore[import]

# Django.
from django.db.backends.postgresql import base
from django.db.backends.utils import CursorWrapper


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences
class CursorDebugWrapper(base.CursorDebugWrapper):  # type: ignore[name-defined,misc]
  """Custom debug wrapper."""

  @contextmanager  # type: ignore[arg-type]
  def debug_sql(  # type: ignore[misc]
      self,
      sql: Optional[str] = None,
      params: Optional[Sized] = None,
      use_last_executed_query: bool = False,
      many: bool = False,
  ) -> None :
    """Customize SQL logging."""
    start = time.monotonic_ns()
    try:
      yield
    finally:
      stop = time.monotonic_ns()
      duration_in_nanoseconds = stop - start
      if use_last_executed_query:
        sql = self.db.ops.last_executed_query(self.cursor, sql, params)
      try:
        times = len(params) if many else ''  # type: ignore[arg-type]
      except TypeError:
        # params could be an iterator.
        times = '?'
      if 'SAVEPOINT' not in sql:  # type: ignore[operator]
        tables = sql_metadata.get_query_tables(sql)
        self.db.queries_log.append({
            'time': duration_in_nanoseconds // 1000,  # type: ignore[dict-item]
            'operation': sql.split(maxsplit = 1)[0],  # type: ignore[union-attr]
            'main_table': tables[0] if len(tables) > 0 else None,
            'join_tables': ', '.join(tables[1:]) if len(tables) > 1 else None,
            'sql': f'{times} times: {sql}' if many else sql,
        })


class DatabaseWrapper(base.DatabaseWrapper):
  """Custom database backend to enable SQL logging."""

  def __init__(self, *args: Any, **kwargs: Any) -> None :
    """Enforce debug logging."""
    super().__init__(*args, **kwargs)
    self.force_debug_cursor = True

  def make_debug_cursor(self, cursor: CursorWrapper) -> CursorDebugWrapper :
    """Replace by custom cursor wrapper."""
    return CursorDebugWrapper(cursor, self)
