"""Custom database backend. THE FILE NAME IS ESSENTIAL!"""

# Python.
import sql_metadata
import time
from contextlib import contextmanager
from typing import Any

# Django.
from django.db.backends.postgresql import base
from django.db.backends.utils import CursorWrapper


class CursorDebugWrapper(base.CursorDebugWrapper):
  """Custom debug wrapper."""

  @contextmanager
  def debug_sql(
      self,
      sql = None,
      params = None,
      use_last_executed_query = False,
      many = False,
  ) -> None :
    """Customize SQL logging."""
    start = time.monotonic_ns()
    try:
      yield
    finally:
      stop = time.monotonic_ns()
      duration = stop - start
      if use_last_executed_query:
        sql = self.db.ops.last_executed_query(self.cursor, sql, params)
      try:
        times = len(params) if many else ''
      except TypeError:
        # params could be an iterator.
        times = '?'
      if 'SAVEPOINT' not in sql:
        tables = sql_metadata.get_query_tables(sql)
        self.db.queries_log.append({
            'time': duration,
            'operation': sql.split(maxsplit = 1)[0],
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
