"""Test the default manager."""

# Python.
from datetime import timedelta
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import LogRequest, LogQuery
from common.models.log.query.operation_type import Operation
from test_util.models.log.request import TestLogRequestIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


class LogQueryDefaultManagerUnitTests(SimpleTestCase):
  """Unit tests for the default manager."""

  def test_create(self) -> None :
    """Test if creation works."""
    for operation in Operation:
      for join_table in [None, 'join_table']:
        with patch.object(LogQuery.objects, 'model', return_value = MagicMock()) as model:
          with self.subTest(operation = operation, join_table = join_table):
            # Perform test.
            LogQuery.objects.create(
                request = LogRequest(),
                time = 1000000,  # 1 second in microseconds.
                operation = operation.name,
                main_table = 'main_table',
                join_table = join_table,
                sql = 'some sql query'
            )
            # Assert result.
            model.return_value.save.assert_called_once_with()


class LogQueryDefaultManagerIntegrationTests(TestCase, TestLogRequestIntegrationMixin):
  """Unit tests for the default manager."""

  def test_create_and_get_full_input(self) -> None :
    """Test if creation works."""
    # Prepare data.
    request = LogRequest.objects.create_and_get(**self.create_and_get_minimum_input())
    time = 1000000  # 1 second in microseconds.
    main_table = 'main_table'
    sql = 'some sql query'
    for operation in Operation:
      for join_table in [None, 'join_table']:
        with self.subTest(operation = operation, join_table = join_table):
          # Perform test.
          LogQuery.objects.create(
              request = request,
              time = time,  # 1 second in microseconds.
              operation = operation.name,
              main_table = main_table,
              join_table = join_table,
              sql = sql
          )
          # Assert result.
          log = LogQuery.objects.get()
          self.assertEqual(request, log.request)
          self.assertEqual(timedelta(microseconds = time), log.time)
          self.assertEqual(operation.name, log.operation)
          self.assertEqual(main_table, log.main_table)
          self.assertEqual(join_table, log.join_table)
          self.assertEqual(sql, log.sql)
          log.delete()
