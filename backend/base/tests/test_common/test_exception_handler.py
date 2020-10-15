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
from common.exception_handler import exception_handler
from common.exceptions import KhaleesiException, TeapotException
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


class ExceptionHandlerUnitTests(ExceptionHandlerMixin, SimpleTestCase):
  """The unit tests for exception handling."""

  def test_khaleesi_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(KhaleesiException):
      with self.subTest(exception = exception_type):
        try:
          exception = exception_type()
          response = exception_handler(
              exception = exception,
              context = {},
          )
          # noinspection PyUnresolvedReferences
          self.assertEqual(exception.data, response.data)  # type: ignore[union-attr]
          # noinspection PyUnresolvedReferences
          self.assertEqual(exception.code, response.status_code)  # type: ignore[union-attr]
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  @patch('common.exception_handler.rest_exception_handler')
  def test_django_rest_exception_handling(
      self,
      rest_exception_handler: MagicMock,
  ) -> None :
    """Test if exception responses get built correctly."""
    counter = 0
    for exception_type in self.get_all_exceptions(APIException):
      with self.subTest(exception = exception_type):
        try:
          exception = exception_type()
          response = exception_handler(exception = exception, context = {})
          # noinspection PyUnresolvedReferences
          self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]
        except TypeError:  # Some exceptions have no empty constructor.
          counter += 1
    self.assertEqual(
        len(self.get_all_exceptions(APIException)) - counter,
        rest_exception_handler.call_count,
    )

  @patch('common.exception_handler.rest_exception_handler')
  def test_django_exception_handling(
      self,
      rest_exception_handler: MagicMock,
  ) -> None :
    """Test if exception responses get built correctly."""
    response = exception_handler(exception = PermissionDenied(), context = {})
    # noinspection PyUnresolvedReferences
    self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]
    self.assertEqual(1, rest_exception_handler.call_count)


class ExceptionHandlerIntegrationTests(ExceptionHandlerMixin, TestCase):
  """The integration tests for exception handling."""

  def test_khaleesi_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(KhaleesiException):
      with self.subTest(exception = exception_type):
        try:
          exception = exception_type()
          response = exception_handler(
              exception = exception,
              context = {},
          )
          # noinspection PyUnresolvedReferences
          self.assertEqual(exception.data, response.data)  # type: ignore[union-attr]
          # noinspection PyUnresolvedReferences
          self.assertEqual(exception.code, response.status_code)  # type: ignore[union-attr]
          if isinstance(exception, TeapotException):
            # noinspection PyUnresolvedReferences
            self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code) # type: ignore[attr-defined,union-attr]
          else:
            # noinspection PyUnresolvedReferences
            self.assertNotEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code) # type: ignore[attr-defined,union-attr]
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  def test_django_rest_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(APIException):
      with self.subTest(exception = exception_type):
        try:
          exception = exception_type()
          response = exception_handler(
              exception = exception,
              context = {},
          )
          self.assertIsNotNone(response)
          # noinspection PyUnresolvedReferences
          self.assertIsNotNone(response.data)  # type: ignore[union-attr]
          # noinspection PyUnresolvedReferences
          self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  # noinspection PyUnresolvedReferences
  def test_django_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    response = exception_handler(exception = PermissionDenied(), context = {})
    self.assertIsNotNone(response)
    # noinspection PyUnresolvedReferences
    self.assertIsNotNone(response.data)  # type: ignore[union-attr]
    self.assertEqual(status.HTTP_418_IM_A_TEAPOT, response.status_code)  # type: ignore[union-attr,attr-defined]

  def test_not_found_exception_handling(self) -> None :
    """Test if built-in 404s are handled correctly."""
    for exception_type in [Http404, NotFound]:
      with self.subTest(exception = exception_type):
        exception = exception_type()
        response = exception_handler(exception = exception, context = {})
        self.assertIsNotNone(response)
        # noinspection PyUnresolvedReferences
        self.assertIsNotNone(response.data)  # type: ignore[union-attr]
        # noinspection PyUnresolvedReferences
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)  # type: ignore[union-attr,attr-defined]
