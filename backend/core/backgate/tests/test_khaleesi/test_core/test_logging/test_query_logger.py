"""Test query logger."""

# Python.
from typing import Any, cast
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.query_logger import QueryLogger, query_logger
from khaleesi.core.logging.text_logger import LogLevel
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.shared.state import STATE
from khaleesi.core.test_util.exceptions import khaleesi_raising_method, exception_raising_method
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

  def test_call_khaleesi_exception(self) -> None :
    """Test calling the query logger."""
    for many in [ True, False ]:
      for status in StatusCode:
        for loglevel in LogLevel:
          with self.subTest(many = many, status = status.name, loglevel = loglevel.name):
            # Prepare data.
            alias = 'test'
            sql = 'sql'
            logger = QueryLogger(alias = alias)
            method = khaleesi_raising_method(status = status, loglevel = loglevel)
            STATE.reset()
            STATE.queries[alias] = []
            self.assertEqual(0, len(STATE.queries[alias]))
            # Execute test.
            with self.assertRaises(KhaleesiException) as exception:
              logger(execute = method, sql = sql, params = None, many = many, context = {})
              # Assert result.
              khaleesi_exception = cast(KhaleesiException, exception)
              self.assertEqual(1, len(STATE.queries[alias]))
              self.assertEqual(sql, STATE.queries[alias][0].raw)
              self.assertIsNotNone(STATE.queries[alias][0].query_id)
              self.assertEqual(status  , khaleesi_exception.status)  # pylint: disable=no-member
              self.assertEqual(loglevel, khaleesi_exception.loglevel)  # pylint: disable=no-member

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
        with self.assertRaises(Exception) as exception:
          logger(execute = method, sql = sql, params = None, many = many, context = {})
          # Assert result.
          khaleesi_exception = cast(KhaleesiException, exception)
          self.assertEqual(1, len(STATE.queries[alias]))
          self.assertEqual(sql, STATE.queries[alias][0].raw)
          self.assertIsNotNone(STATE.queries[alias][0].query_id)
          self.assertEqual(StatusCode.INTERNAL, khaleesi_exception.status)  # pylint: disable=no-member
          self.assertEqual(LogLevel.FATAL     , khaleesi_exception.loglevel)  # pylint: disable=no-member


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
