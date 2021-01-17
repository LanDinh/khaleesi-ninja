"""Custom database backend. THE FILE NAME IS ESSENTIAL!"""

# Python.
import re
import time
from contextlib import contextmanager
from typing import Any, Optional, Sized

# Django.
from django.db.backends.postgresql.base import (
    DatabaseWrapper as DjangoDatabaseWrapper,
    CursorDebugWrapper as DjangoCursorDebugWrapper
)
from django.db.backends.utils import CursorWrapper
import sql_metadata


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences
class CursorDebugWrapper(DjangoCursorDebugWrapper):  # type: ignore[name-defined,misc]
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
    if 'SAVEPOINT' not in sql:
      with super().debug_sql(sql, params, use_last_executed_query, many):
        start = time.monotonic_ns()
        yield
        stop = time.monotonic_ns()
      nanoseconds = stop - start
      self.db.queries_log[-1]['nanoseconds'] = nanoseconds
    else:
      yield


class DatabaseWrapper(DjangoDatabaseWrapper):
  """Custom database backend to enable SQL logging."""

  def __init__(self, *args: Any, **kwargs: Any) -> None :
    """Enforce debug logging."""
    super().__init__(*args, **kwargs)
    self.force_debug_cursor = True

  def make_debug_cursor(self, cursor: CursorWrapper) -> CursorDebugWrapper :
    """Replace by custom cursor wrapper."""
    return CursorDebugWrapper(cursor, self)
