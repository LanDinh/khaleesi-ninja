"""Test the default manager."""

# Python.
from datetime import timedelta
from typing import List, Tuple, Optional
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import LogRequest, LogQuery
from test_util.models.log.request import TestLogRequestIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


class TestLogQueryDefaultManagerMixin:
  """Parameters for better testing."""

  @staticmethod
  def params(*, main: str) -> List[Tuple[str, Optional[str], str]] :
    """Parameters for better testing."""
    return [
        ('SELECT', None, f'SELECT * FROM {main}'),
        ('INSERT', None, f'INSERT INTO {main} VALUES (test)'),
        ('UPDATE', None, f'UPDATE {main} SET test = foo WHERE test = bar'),
        ('DELETE', None, f'DELETE FROM {main} WHERE test = foo'),
        (
            'SELECT',
            'secondary',
            f'SELECT * FROM {main} INNER JOIN secondary ON {main}.test = secondary.test'
        ),
        (
            'UPDATE',
            'secondary',
            f'UPDATE {main} SET test = foo FROM secondary WHERE {main}.test = secondary.test'
        ),
        (
            'DELETE',
            'secondary',
            f'DELETE FROM {main} WHERE id IN (SELECT id FROM secondary WHERE secondary.test = foo)'
        ),
    ]


class LogQueryDefaultManagerUnitTests(TestLogQueryDefaultManagerMixin, SimpleTestCase):
  """Unit tests for the default manager."""

  def test_create(self) -> None :
    """Test if creation works."""
    # Prepare data.
    request = LogRequest()
    main = 'main'
    for operation, join, sql in self.params(main = main):
      with self.subTest(operation = operation, join = join):
        with patch.object(LogQuery.objects, 'model') as model:
          model.return_value = MagicMock()
          model.return_value.save = MagicMock()
          # Perform test.
          LogQuery.objects.create(request = request, nanoseconds = 1234, sql = sql)
          # Assert result.
          model.assert_called_once_with(
              request = request,
              time = timedelta(microseconds=1),
              operation = operation,
              main_table = main,
              join_table = join,
              sql = sql,
          )
          model.return_value.save.assert_called_once_with()


class LogQueryDefaultManagerIntegrationTests(
    TestLogQueryDefaultManagerMixin,
    TestLogRequestIntegrationMixin,
    TestCase,
):
  """Unit tests for the default manager."""

  def test_create(self) -> None :
    """Test if creation works."""
    # Prepare data.
    request = LogRequest.objects.create_and_get(**self.create_and_get_minimum_input())
    main = 'main'
    for operation, join, sql in self.params(main = main):
      with self.subTest(operation = operation, join = join):
        # Perform test.
        LogQuery.objects.create(request = request, nanoseconds = 1234, sql = sql)
        # Assert result.
        log = LogQuery.objects.get()
        self.assertEqual(request, log.request)
        self.assertEqual(timedelta(microseconds = 1), log.time)
        self.assertEqual(operation, log.operation)
        self.assertEqual(main, log.main_table)
        self.assertEqual(join, log.join_table)
        self.assertEqual(sql, log.sql)
        log.delete()
