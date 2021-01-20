"""Exception information."""

# Python.
from __future__ import annotations

# Django.
import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

# khaleesi.ninja.
from django.forms.models import model_to_dict
from django.utils import timezone

from common.models.user.model import User
from common.models.log.request.manager_default import DefaultManager
from common.models.model import Model, choices
from common.service_type import ServiceType


logger = logging.getLogger('khaleesi')

class LogRequest(Model):
  """Client information."""

  # Client information - ready before processing.
  start_time = models.DateTimeField(auto_now_add = True)
  client_id = models.UUIDField(blank = True, null = True)
  language = models.CharField(max_length = 2, blank = True, null = True)

  # Request information backend - ready before processing.
  backend_route = models.TextField()
  backend_parameters = models.TextField()
  backend_service = models.CharField(max_length = 50, choices = choices(ServiceType))
  backend_feature = models.CharField(max_length = 50)
  backend_body = models.TextField()

  # Request information frontend - ready before processing.
  frontend_route = models.TextField()
  frontend_parameters = models.TextField()
  frontend_service = models.CharField(max_length = 50, choices = choices(ServiceType))
  frontend_feature = models.CharField(max_length = 50)
  frontend_body = models.TextField()

  # Processed information - ready after processing.
  user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
  end_time = models.DateTimeField(blank = True, null = True)

  # Response information - ready after processing.
  response_code = models.IntegerField(blank = True, null = True)

  objects: DefaultManager[LogRequest] = DefaultManager()

  def finalize(self, *, user: User, response_code: int) -> None:
    """Finalize the request log."""
    self.user = User.objects.db_manager('logging').get(username = user.username)
    self.response_code = response_code
    self.end_time = timezone.now()
    logger.info(json.dumps(model_to_dict(self), cls = DjangoJSONEncoder))
    self.save()
