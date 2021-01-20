"""Default Manager."""

# pylint: disable=line-too-long

# Python.
import json
import logging
import re
from datetime import timedelta
# noinspection SyntaxError,PyMissingOrEmptyDocstring,PyUnresolvedReferences
import sql_metadata  # type: ignore[import]

# Django.
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict

# khaleesi.ninja.
from common.models.log.request.model import LogRequest
from common.models.manager import  Manager, T


logger = logging.getLogger('khaleesi')


class DefaultManager(Manager[T]):
  """Default Manager."""

  # noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring,PyTypeHints,SyntaxError
  def create(self, *, request: LogRequest, nanoseconds: int, sql: str) -> None :  # type: ignore[override]
    """Create a new query log."""
    cleaned_sql = self._clean_sql(sql = sql)
    tables = sql_metadata.get_query_tables(cleaned_sql)
    log = self.model(
        request = request,
        microseconds = timedelta(microseconds = nanoseconds // 1000),
        operation = cleaned_sql.split(maxsplit = 1)[0],
        main_table = tables[0] if len(tables) > 0 else None,
        join_table = ', '.join(tables[1:]) if len(tables) > 1 else None,
        sql_generalized = sql_metadata.generalize_sql(cleaned_sql),
        sql_specific = cleaned_sql,
    )
    logger.debug(json.dumps(model_to_dict(log), cls = DjangoJSONEncoder))
    log.save()

  @staticmethod
  def _clean_sql(*, sql: str) -> str :
    cleaned_sql = sql
    for table in sql_metadata.get_query_tables(sql):
      cleaned_sql = re.sub(fr'"{table}"."(?P<column>[a-z_]+)"', fr'{table}.\g<column>', cleaned_sql)
      cleaned_sql = re.sub(fr'"{table}"', table, cleaned_sql)
    return cleaned_sql
