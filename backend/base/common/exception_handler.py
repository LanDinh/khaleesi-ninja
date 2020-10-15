"""Custom exception handling."""

# pylint: disable=line-too-long

# Python.
from typing import Any, Dict, Optional

# Django.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as rest_exception_handler

# khaleesi.ninja.
from common.exceptions import KhaleesiException


def exception_handler(
    exception: Exception,
    context: Dict[str, Any]
) -> Optional[Response] :
  """Handle custom exceptions."""
  if isinstance(exception, KhaleesiException):
    return Response(data = exception.data, status = exception.code)
  response = rest_exception_handler(exception, context)
  if not response or response.status_code == status.HTTP_404_NOT_FOUND:
    return response
  # noinspection PyTypeHints,PyUnresolvedReferences
  response.status_code = status.HTTP_418_IM_A_TEAPOT  # type: ignore[attr-defined]
  return response
