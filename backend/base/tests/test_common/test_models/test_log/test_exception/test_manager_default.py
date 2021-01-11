"""The tests for the custom exception handler."""

# pylint: disable=line-too-long

# Python.
from functools import reduce
from operator import add
from typing import List
from unittest.mock import MagicMock

# Django.
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.exceptions import APIException, NotFound

# khaleesi.ninja
from common.models import LogException
from common.exceptions import KhaleesiException
from test_util.test import SimpleTestCase, TestCase


class LogExceptionDefaultManagerMixin:
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
class LogExceptionDefaultManagerUnitTests(LogExceptionDefaultManagerMixin, SimpleTestCase):
  """The unit tests for exception handling."""

  def test_khaleesi_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(KhaleesiException):
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          log = self.setup_model()
          # Perform test.
          LogException.objects.create_khaleesi(exception = exception)
          # Assert result.
          self.assertEqual(exception.code, log.http_code)
          log.save.assert_called_once_with()
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  def test_django_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type\
        in self.get_all_exceptions(APIException) + [PermissionDenied, Http404, NotFound]:
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          log = self.setup_model()
          # Perform test.
          LogException.objects.create_extern(exception = exception)
          # Assert result.
          log.save.assert_called_once_with()
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  @staticmethod
  def setup_model() -> MagicMock :
    """Setup the model mocks"""
    log = MagicMock()
    log.save = MagicMock()
    LogException.objects.model = MagicMock(return_value = log)
    return log


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class LogExceptionDefaultManagerIntegrationTests(LogExceptionDefaultManagerMixin, TestCase):
  """The integration tests for exception handling."""

  def test_khaleesi_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(KhaleesiException):
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          # Perform test.
          LogException.objects.create_khaleesi(exception = exception)
          # Assert result.
          log = LogException.objects.get()
          self.assertEqual(exception.code, log.http_code)
          log.delete()
        except TypeError:  # Some exceptions have no empty constructor.
          pass

  def test_django_exception_handling(self) -> None :
    """Test if exception responses get built correctly."""
    for exception_type in self.get_all_exceptions(APIException) + [PermissionDenied, Http404, NotFound]:
      with self.subTest(exception = exception_type):
        try:
          # Prepare data.
          exception = exception_type()
          # Perform test.
          LogException.objects.create_extern(exception = exception)
          # Assert result.
          log = LogException.objects.get()
          self.assertIsNone(log.http_code)
          log.delete()
        except TypeError:  # Some exceptions have no empty constructor.
          pass
