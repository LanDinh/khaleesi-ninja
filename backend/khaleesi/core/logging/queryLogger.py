"""Log query data."""

# Python.
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator

# Django.
from django.db import connection

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_sawmill_pb2 import Query


class QueryLogger:
  """Log query data."""

  def __call__(
      self,
      execute: Callable[[str, Any, bool, Dict[str, Any]], Any],
      sql    : str,
      params : Any,
      many   : bool,
      context: Dict[str, Any],
  ) -> Any :
    """Wrap the database call."""
    query = Query()
    query.raw = sql
    query.start.FromDatetime(datetime.now(tz = timezone.utc))
    STATE.queries.append(query)

    try:
      result = execute(sql, params, many, context)
      return result  # finally executes before the return statement.
    finally:
      query.end.FromDatetime(datetime.now(tz = timezone.utc))


@contextmanager
def queryLogger() -> Generator[None, None, None] :
  """Context manager for query logger."""

  with connection.execute_wrapper(QueryLogger()):
    yield
