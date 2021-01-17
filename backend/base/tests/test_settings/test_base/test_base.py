"""Test custom database engine."""

# Python.
from unittest.mock import MagicMock

# Django.
from django.db import connection, reset_queries

# khaleesi.ninja.
from settings.base import CursorDebugWrapper
from test_util.test import SimpleTestCase, TestCase
from .models import TestModel


class CursorDebugWrapperUnitTests(SimpleTestCase):
  """Test custom cursor wrapper."""

  cursor = CursorDebugWrapper(MagicMock(), MagicMock())

  def test_debug_sql_no_join(self) -> None :
    """Test debug_sql."""
    # Prepare data.
    self.cursor.db.queries_log = []
    # Perform test.
    with self.cursor.debug_sql(sql = 'some sql statement'):
      pass
    # Assert result.
    self.assertIsNotNone(self.cursor.db.queries_log[0]['nanoseconds'])


class CursorDebugWrapperIntegrationTests(TestCase):
  """Test custom cursor wrapper."""

  def test_debug_sql(self) -> None :
    """Test debug_sql."""
    # Prepare data.
    reset_queries()
    # Perform test.
    TestModel.objects.get_queryset().create()
    # Assert result.
    self.assertEqual(1, len(connection.queries))
    self.assertIsNotNone(connection.queries[0]['nanoseconds'])
    reset_queries()
