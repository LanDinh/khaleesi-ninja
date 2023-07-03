"""Log query data."""

# Python.
from contextlib import contextmanager, ExitStack
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator
from uuid import uuid4

# Django.
from django.db import connections

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE
from khaleesi.proto.core_sawmill_pb2 import Query


class QueryLogger:
  """Log query data."""

  alias: str

  def __init__(self, *, alias: str) -> None :
    """Initialize."""
    self.alias = alias

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
    query.id         = str(uuid4())
    query.connection = self.alias
    query.raw        = sql
    query.start.FromDatetime(datetime.now(tz = timezone.utc))
    STATE.queries.append(query)

    try:
      result = execute(sql, params, many, context)
      return result  # finally executes before the return statement.
    finally:
      query.end.FromDatetime(datetime.now(tz = timezone.utc))


@contextmanager
def queryLogger() -> Generator[Dict[str, QueryLogger], None, None] :
  """Context manager for query logger."""

  queryLoggers = {}
  with ExitStack() as stack:
    for alias in connections:
      logger = QueryLogger(alias = alias)
      queryLoggers[alias] = logger
      # noinspection PyTypeChecker
      stack.enter_context(connections[alias].execute_wrapper(logger))
    yield queryLoggers
