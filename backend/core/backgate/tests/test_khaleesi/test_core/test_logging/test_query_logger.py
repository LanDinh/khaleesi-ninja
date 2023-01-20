"""Test query logger."""

# Python.
from typing import Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.logging.query_logger import QueryLogger, query_logger
from khaleesi.core.shared.state import STATE
from khaleesi.core.test_util.exceptions import exception_raising_method
from khaleesi.core.test_util.test_case import SimpleTestCase

class QueryLoggerTestCase(SimpleTestCase):
  """Test the query logger."""

  def test_call(self) -> None :
    """Test calling the query logger."""
    for many in [ True, False ]:
      with self.subTest(many = many):
        # Prepare data.
        alias = 'test'
        sql = 'sql'
        logger = QueryLogger(alias = alias)
        def method(*_: Any) -> None :
          pass
        STATE.reset()
        STATE.queries[alias] = []
        self.assertEqual(0, len(STATE.queries[alias]))
        # Execute test.
        logger(execute = method, sql = sql, params = None, many = many, context = {})
        # Assert result.
        self.assertEqual(1, len(STATE.queries[alias]))
        self.assertEqual(sql, STATE.queries[alias][0].raw)
        self.assertIsNotNone(STATE.queries[alias][0].query_id)

  def test_call_other_exception(self) -> None :
    """Test calling the query logger."""
    for many in [ True, False ]:
      with self.subTest(many = many):
        # Prepare data.
        alias = 'test'
        sql = 'sql'
        logger = QueryLogger(alias = alias)
        method = exception_raising_method()
        STATE.reset()
        STATE.queries[alias] = []
        self.assertEqual(0, len(STATE.queries[alias]))
        # Execute test.
        with self.assertRaises(Exception):
          logger(execute = method, sql = sql, params = None, many = many, context = {})
          # Assert result.
          self.assertEqual(1, len(STATE.queries[alias]))
          self.assertEqual(sql, STATE.queries[alias][0].raw)
          self.assertIsNotNone(STATE.queries[alias][0].query_id)


class QueryLoggerContextManagerTestCase(SimpleTestCase):
  """Test the query logger context manager."""

  @patch('khaleesi.core.logging.query_logger.ExitStack')
  def test_context_manager(self, _: MagicMock) -> None :
    """Test the context manager."""
    # Execute test.
    with query_logger() as logger:
      # Assert result.
      self.assertEqual(3, len(logger))
      self.assertIn('default', logger)
