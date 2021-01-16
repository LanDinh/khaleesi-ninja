"""Test custom database engine."""

# Python.
from unittest.mock import MagicMock

# Django.
from django.db import connection

# khaleesi.ninja.
from settings.base import CursorDebugWrapper
from test_util.test import SimpleTestCase, TestCase
from .models import TestModel


class CursorDebugWrapperUnitTests(SimpleTestCase):
  """Test custom cursor wrapper."""

  cursor = CursorDebugWrapper(MagicMock(), MagicMock())

  def test_debug_sql_skips_savepoint_queries(self) -> None :
    """Test debug_sql."""
    # Prepare data.
    self.cursor.db.queries_log = MagicMock()
    self.cursor.db.queries_log.append = MagicMock()
    # Perform test.
    with self.cursor.debug_sql(sql = 'SAVEPOINT name'):
      pass
    # Assert result.
    self.cursor.db.queries_log.append.assert_not_called()

  def test_debug_sql_no_join(self) -> None :
    """Test debug_sql."""
    # Prepare data.
    queries = MagicMock()
    self.cursor.db.queries_log = MagicMock()
    self.cursor.db.queries_log.append = queries
    operation = 'SELECT'
    main_table = 'test_table'
    sql = f'{operation} * FROM {main_table}'
    # Perform test.
    with self.cursor.debug_sql(sql = sql):
      pass
    # Assert result.
    queries.assert_called_once()
    args, kwargs = queries.call_args
    self.assertEqual({}, kwargs)
    self.assertGreater(1000000, args[0]['time'])  # 1 second in microseconds.
    self.assertLessEqual(0, args[0]['time'])
    self.assertEqual(operation, args[0]['operation'])
    # noinspection SpellCheckingInspection
    self.assertEqual(main_table, args[0]['main_table'])
    self.assertIsNone(args[0]['join_tables'])
    self.assertEqual(sql, args[0]['sql'])

  def test_debug_sql_with_join(self) -> None :
    """Test debug_sql."""
    # Prepare data.
    queries = MagicMock()
    self.cursor.db.queries_log = MagicMock()
    self.cursor.db.queries_log.append = queries
    operation = 'DELETE'
    main_table = 'main_table'
    join_table = 'join_table'
    sql = f'{operation} FROM {main_table} WHERE {main_table}.a IN (SELECT a FROM {join_table})'
    # Perform test.
    with self.cursor.debug_sql(sql = sql):
      pass
    # Assert result.
    queries.assert_called_once()
    args, kwargs = queries.call_args
    self.assertEqual({}, kwargs)
    self.assertGreater(1000000, args[0]['time'])  # 1 second in microseconds.
    self.assertLessEqual(0, args[0]['time'])
    self.assertEqual(operation, args[0]['operation'])
    # noinspection SpellCheckingInspection
    self.assertEqual(main_table, args[0]['main_table'])
    self.assertEqual(join_table, args[0]['join_tables'])
    self.assertEqual(sql, args[0]['sql'])


class CursorDebugWrapperIntegrationTests(TestCase):
  """Test custom cursor wrapper."""

  def test_debug_sql(self) -> None :
    """Test debug_sql."""
    # Perform test.
    TestModel.objects.get_queryset().create()
    # Assert result.
    self.assertEqual(1, len(connection.queries))
    self.assertGreater(1000000, connection.queries[0]['time'])  # 1 second in microseconds.
    self.assertLessEqual(0, connection.queries[0]['time'])
    self.assertEqual('INSERT', connection.queries[0]['operation'])
    # noinspection SpellCheckingInspection
    self.assertEqual('test_base_settings_base_testmodel', connection.queries[0]['main_table'])
    self.assertIsNone(connection.queries[0]['join_tables'])
