"""Default Manager."""

# Python.
import json
import logging
import traceback

# khaleesi.ninja.
from typing import Optional

from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from rest_framework.response import Response

from common.exceptions import KhaleesiException
from common.models.log.request.model import LogRequest
from common.models.manager import  Manager, T


logger = logging.getLogger('khaleesi')


class DefaultManager(Manager[T]):
  """Default Manager."""

  # noinspection PyUnresolvedReferences,PyTypeHints,PyMissingOrEmptyDocstring
  def create_khaleesi(self, *, request: LogRequest, exception: KhaleesiException) -> None :
    """Create a new exception log."""
    log = self._create(request = request, exception = exception)
    log.http_code = exception.code  # type: ignore[attr-defined]
    log.data = str(exception.data)  # type: ignore[attr-defined]
    logger.error(json.dumps(model_to_dict(log)))
    log.save()

  # noinspection PyMissingOrEmptyDocstring,PyTypeHints,PyUnresolvedReferences
  def create_extern(
      self, *,
      request: LogRequest,
      response: Optional[Response] = None,
      exception: Exception,
  ) -> None :
    """Create a new exception log."""
    log = self._create(request = request, exception = exception)
    if response:
      log.http_code = response.status_code  # type: ignore[attr-defined]
    logger.error(json.dumps(model_to_dict(log), cls = DjangoJSONEncoder))
    log.save()

  def _create(self, *, request: LogRequest, exception: Exception) -> T :
    tb_exception = traceback.TracebackException.from_exception(exception)
    log = self.model(
        request = request,
        exception = tb_exception.exc_type.__name__,
        message = str(exception),
        stacktrace = ''.join(tb_exception.format()),
    )
    return log
