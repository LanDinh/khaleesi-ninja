"""Exception information."""

# Django.
from django.db import models

# khaleesi.ninja.
from common.models.log.exception.manager_default import DefaultManager
from common.models.model import Model


class LogException(Model):
  """Exception information."""

  # Generic attributes.
  exception = models.CharField(max_length = 50)
  timestamp = models.DateTimeField(auto_now_add = True)
  message = models.TextField(blank = True)
  stacktrace = models.TextField()

  # khaleesi.ninja specific attributes.
  http_code = models.IntegerField(blank = True, null = True)
  data = models.TextField(blank = True)

  objects = DefaultManager()
