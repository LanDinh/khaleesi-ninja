"""Log query data."""

# Python.
from contextlib import contextmanager, ExitStack
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Generator
from uuid import uuid4

# Django.
from django.db import connections

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import KhaleesiException, MaskingInternalServerException
from khaleesi.core.shared.state import Query, STATE


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
    query = Query(query_id = str(uuid4()), raw = sql, start = datetime.now(tz = timezone.utc))
    STATE.queries[self.alias].append(query)
    try:
      result = execute(sql, params, many, context)
      return result  # finally executes before the return statement.
    except KhaleesiException:
      raise
    except Exception as exception:
      raise MaskingInternalServerException(exception = exception) from exception
    finally:
      query.end = datetime.now(tz = timezone.utc)


@contextmanager
def query_logger() -> Generator[Dict[str, QueryLogger], None, None] :
  """Context manager for query logger."""

  query_loggers = {}
  with ExitStack() as stack:
    for alias in connections:
      logger = QueryLogger(alias = alias)
      query_loggers[alias] = logger
      # noinspection PyTypeChecker
      stack.enter_context(connections[alias].execute_wrapper(logger))
    yield query_loggers
