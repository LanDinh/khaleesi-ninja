"""Database query information."""

# Python.
from __future__ import annotations

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.log.query.operation_type import Operation
from common.models.log.query.manager_default import DefaultManager
from common.models.log.request.model import LogRequest
from common.models.model import Model, choices


class LogQuery(Model):
  """Database query information."""

  request = models.ForeignKey(LogRequest, on_delete = models.CASCADE)
  time = models.DurationField()
  operation = models.CharField(max_length = 50, choices = choices(Operation))
  main_table = models.CharField(max_length = 50)
  join_table = models.TextField(blank = True, null = True)
  sql = models.TextField()

  objects: DefaultManager[LogQuery] = DefaultManager()
