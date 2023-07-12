"""Test query logger."""

# Python.
from typing import Any
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.logging.queryLogger import QueryLogger, queryLogger
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.testCase import SimpleTestCase

class QueryLoggerTestCase(SimpleTestCase):
  """Test the query logger."""

  def testCall(self) -> None :
    """Test calling the query logger."""
    for many in [ True, False ]:
      with self.subTest(many = many):
        # Prepare data.
        sql = 'sql'
        logger = QueryLogger()
        def method(*_: Any) -> None :
          pass
        STATE.reset()
        self.assertEqual(0, len(STATE.queries))
        # Execute test.
        logger(execute = method, sql = sql, params = None, many = many, context = {})
        # Assert result.
        self.assertEqual(1, len(STATE.queries))
        self.assertEqual(sql, STATE.queries[0].raw)
        self.assertIsNotNone(STATE.queries[0].id)


class QueryLoggerContextManagerTestCase(SimpleTestCase):
  """Test the query logger context manager."""

  def testContextManager(self) -> None :
    """Test the context manager."""
    # Execute test.
    with queryLogger():
      # Assert result.
      self.assertTrue(True)
