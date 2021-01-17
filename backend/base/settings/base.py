"""Custom database backend. THE FILE NAME IS ESSENTIAL!"""

# Python.
import sys
import time
from contextlib import contextmanager
from typing import Any, Optional, Sized

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
    context = super().debug_sql(sql, params, use_last_executed_query, many)
    start = time.monotonic_ns()
    context.__enter__()  # pylint: disable=no-member
    yield
    context.__exit__(*sys.exc_info())  # pylint: disable=no-member
    stop = time.monotonic_ns()
    nanoseconds = stop - start
    self.db.queries_log[-1]['nanoseconds'] = nanoseconds


class DatabaseWrapper(base.DatabaseWrapper):
  """Custom database backend to enable SQL logging."""

  def __init__(self, *args: Any, **kwargs: Any) -> None :
    """Enforce debug logging."""
    super().__init__(*args, **kwargs)
    self.force_debug_cursor = True

  def make_debug_cursor(self, cursor: CursorWrapper) -> CursorDebugWrapper :
    """Replace by custom cursor wrapper."""
    return CursorDebugWrapper(cursor, self)
