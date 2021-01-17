"""Database query information."""

# Python.
from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.log.query.manager_default import DefaultManager
from common.models.log.request.model import LogRequest
from common.models.model import Model


class LogQuery(Model):
  """Database query information."""

  request = models.ForeignKey(LogRequest, on_delete = models.CASCADE)
  microseconds = models.DurationField()
  operation = models.CharField(max_length = 50)
  main_table = models.CharField(max_length = 50)
  join_table = models.TextField(blank = True, null = True)
  sql_generalized = models.TextField()
  sql_specific = models.TextField()

  objects: DefaultManager[LogQuery] = DefaultManager()
