"""The tests for the custom exception handler."""

# pylint: disable=line-too-long

# Python.
from functools import reduce
from operator import add
from typing import List
from unittest.mock import MagicMock, patch

# Django.
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.exceptions import APIException, NotFound
from rest_framework import status

# khaleesi.ninja
from common.exceptions import KhaleesiException, TeapotException
from common.models import LogException
from settings.exception_handler import exception_handler
from test_util.test import SimpleTestCase, TestCase


class ExceptionHandlerMixin:
  """Utility methods to test the exception handler."""

  def get_all_exceptions(self, cls: type) -> List[type] :
    """Return all final subclasses of the given exception recursively."""
    if cls == NotFound:
      return []
    if cls.__subclasses__():
      subclasses = [self.get_all_exceptions(c) for c in cls.__subclasses__()]
      subclasses.append([cls])
      return reduce(add, subclasses)
    return [cls]


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class ExceptionHandlerUnitTests(ExceptionHandlerMixin, SimpleTestCase):
  """The unit tests for exception handling."""

  @patch.object(LogException.objects, 'create_khaleesi')
  def test_khaleesi_exception_handling(self, log: MagicMock) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(KhaleesiException):
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          # Perform test.
          response = exception_handler(exception = exception, context = {})
          # Assert result.
          self.assertEqual(exception.data, response.data)  # type: ignore[union-attr]
          self.assertEqual(exception.code, response.status_code)  # type: ignore[union-attr]
          log.assert_called_once_with(exception = exception)
          log.reset_mock()
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  @patch.object(LogException.objects, 'create_extern')
  @patch('settings.exception_handler.rest_exception_handler')
  def test_django_rest_exception_handling(
      self,
      rest_exception_handler: MagicMock,
      log: MagicMock
  ) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(APIException):
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          context = {}  # type: ignore[var-annotated]
          # Perform test.
          response = exception_handler(exception = exception, context = context)
          # Assert result.
          self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]
          rest_exception_handler.assert_called_once_with(exception, context)
          rest_exception_handler.reset_mock()
          log.assert_called_once_with(exception = exception)
          log.reset_mock()
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  @patch.object(LogException.objects, 'create_extern')
  @patch('settings.exception_handler.rest_exception_handler')
  def test_django_exception_handling(
      self,
      rest_exception_handler: MagicMock,
      log: MagicMock
  ) -> None :
    """Test if exception responses get built correctly."""
    # Prepare data.
    exception = PermissionDenied()
    context = {}  # type: ignore[var-annotated]
    # Perform test.
    response = exception_handler(exception = exception, context = context)
    # Assert result.
    self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]
    rest_exception_handler.assert_called_once_with(exception, context)
    log.assert_called_once_with(exception = exception)

  @patch.object(LogException.objects, 'create_extern')
  @patch('settings.exception_handler.rest_exception_handler')
  def test_not_found_exception_handling(
      self,
      rest_exception_handler: MagicMock,
      log: MagicMock
  ) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in [Http404, NotFound]:
      with self.subTest(exception = exception_type):
        # Prepare data.
        response = MagicMock()
        response.status_code = status.HTTP_404_NOT_FOUND
        rest_exception_handler.return_value = response
        exception = exception_type()
        context = {}  # type: ignore[var-annotated]
        # Perform test.
        result = exception_handler(exception = exception, context = context)
        # Assert result.
        self.assertEqual(status.HTTP_404_NOT_FOUND, result.status_code)  # type: ignore[union-attr,attr-defined]
        rest_exception_handler.assert_called_once_with(exception, context)
        rest_exception_handler.reset_mock()
        log.assert_called_once_with(exception = exception)
        log.reset_mock()


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class ExceptionHandlerIntegrationTests(ExceptionHandlerMixin, TestCase):
  """The integration tests for exception handling."""

  def test_khaleesi_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(KhaleesiException):
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          # Perform test.
          response = exception_handler(exception = exception, context = {})
          # Assert result.
          self.assertEqual(exception.data, response.data)  # type: ignore[union-attr]
          self.assertEqual(exception.code, response.status_code)  # type: ignore[union-attr]
          if isinstance(exception, TeapotException):
            self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code) # type: ignore[attr-defined,union-attr]
          else:
            self.assertNotEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code) # type: ignore[attr-defined,union-attr]
          log = LogException.objects.get(exception = exception.__class__.__name__)
          self.assertEqual(exception.code, log.http_code)
          log.delete()
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  def test_django_rest_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(APIException):
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          # Perform test.
          response = exception_handler(exception = exception, context = {})
          # Assert result.
          self.assertIsNotNone(response)
          self.assertIsNotNone(response.data)  # type: ignore[union-attr]
          self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]
          log = LogException.objects.get(exception = exception.__class__.__name__)
          self.assertIsNone(log.http_code)
          log.delete()
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  def test_django_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    # Prepare data.
    exception = PermissionDenied()
    # Perform test.
    response = exception_handler(exception = exception, context = {})
    # Assert result.
    self.assertIsNotNone(response)
    self.assertIsNotNone(response.data)  # type: ignore[union-attr]
    self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]
    log = LogException.objects.get(exception = exception.__class__.__name__)
    self.assertIsNone(log.http_code)
    log.delete()

  def test_not_found_exception_handling(self) -> None :
    """Test if built-in 404s are handled correctly."""
    for exception_type in [Http404, NotFound]:
      with self.subTest(exception = exception_type):
        # Prepare data.
        exception = exception_type()
        # Perform test.
        response = exception_handler(exception = exception, context = {})
        # Assert result.
        self.assertIsNotNone(response)
        self.assertIsNotNone(response.data)  # type: ignore[union-attr]
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)  # type: ignore[union-attr,attr-defined]
        log = LogException.objects.get(exception = exception.__class__.__name__)
        self.assertIsNone(log.http_code)
        log.delete()
