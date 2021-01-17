"""Test custom database engine."""

# Python.
from unittest.mock import MagicMock, patch

# Django.
from django.db import connection, reset_queries

# khaleesi.ninja.
from settings.base import CursorDebugWrapper, DjangoCursorDebugWrapper
from test_util.test import SimpleTestCase, TestCase
from .models import TestModel


class CursorDebugWrapperUnitTests(SimpleTestCase):
  """Test custom cursor wrapper."""

  cursor = CursorDebugWrapper(MagicMock(), MagicMock())

  @patch.object(DjangoCursorDebugWrapper, 'debug_sql')
  def test_debug_sql_skip_savepoint(self, _: MagicMock) -> None :
    """Test debug_sql."""
    # Prepare data.
    self.cursor.db.queries_log = [{}]
    # Perform test.
    with self.cursor.debug_sql(sql = 'SAVEPOINT some sql statement'):
      pass
    # Assert result.
    self.assertFalse('nanoseconds' in self.cursor.db.queries_log[0])

  @patch.object(DjangoCursorDebugWrapper, 'debug_sql')
  def test_debug_sql_nanoseconds(self, _: MagicMock) -> None :
    """Test debug_sql."""
    # Prepare data.
    self.cursor.db.queries_log = [{}]
    # Perform test.
    with self.cursor.debug_sql(sql = 'some sql statement'):
      pass
    # Assert result.
    self.assertTrue('nanoseconds' in self.cursor.db.queries_log[0])
    self.assertIsNotNone(self.cursor.db.queries_log[0]['nanoseconds'])


class CursorDebugWrapperIntegrationTests(TestCase):
  """Test custom cursor wrapper."""

  def test_debug_sql_skip_savepoint(self) -> None :
    """Test debug_sql."""
    # Prepare data.
    reset_queries()
    # Perform test.
    TestModel.objects.get_queryset().create(name = 'foo')
    TestModel.objects.get_queryset().update_or_create(name = 'foo', defaults = {'name': 'bar'})
    # Assert result.
    # INSERT INTO, SAVEPOINT, SELECT, UPDATE, RELEASE SAVEPOINT
    self.assertEqual(3, len(connection.queries))
    reset_queries()

  def test_debug_sql_nanoseconds(self) -> None :
    """Test debug_sql."""
    # Prepare data.
    reset_queries()
    # Perform test.
    TestModel.objects.get_queryset().create(name = 'foo')
    # Assert result.
    self.assertIsNotNone(connection.queries[0]['nanoseconds'])
    reset_queries()
