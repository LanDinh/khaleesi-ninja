"""Test the core-sawmill lumberjack service."""

# Python.
from typing import Callable, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.exceptions import InvalidArgumentException, InternalServerException
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import LogResponse
from microservice.service.lumberjack import DbEvent, Service  # type: ignore[attr-defined]
from tests.models import Metadata


# noinspection PyMethodMayBeStatic
class LumberjackServiceTestCase(SimpleTestCase):
  """Test the core-sawmill lumberjack service."""

  # pylint: disable=no-self-use

  service = Service()

  def test_log_event(self) -> None :
    """Test logging events."""
    self._execute_logging_tests(
      method = lambda : self.service.LogEvent(MagicMock(), MagicMock()),
      logging_object = DbEvent.objects,
      logging_method = 'log_event',
    )

  def _execute_logging_tests(
      self, *,
      method: Callable[[], LogResponse],
      logging_object: Any,
      logging_method: str,
  ) -> None :
    """Execute all typical logging tests."""
    for test in [
        self._execute_successful_logging_test,
        self._execute_logging_test_with_parsing_error,
        self._execute_logging_test_with_fatal_error
    ]:
      with self.subTest(test = test.__name__):
        with patch.object(logging_object, logging_method) as logging:
          test(method = method, logging = logging)

  def _execute_successful_logging_test(
      self, *,
      method: Callable[[], LogResponse],
      logging: MagicMock,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = Metadata()
    # Execute test.
    method()
    # Assert result.
    logging.assert_called_once()

  def _execute_logging_test_with_parsing_error(
      self, *,
      method: Callable[[], LogResponse],
      logging: MagicMock,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    expected_result = Metadata(meta_logging_errors ='some parsing errors')
    logging.return_value = expected_result
    # Execute test and assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(expected_result.meta_logging_errors, context.exception.private_details)

  def _execute_logging_test_with_fatal_error(
      self, *,
      method: Callable[[], LogResponse],
      logging: MagicMock,
  ) -> None :
    """Call to logging method that results in fatal errors."""
    # Prepare data.
    message = 'fatal exception'
    logging.side_effect = Exception(message)
    # Execute test and assert result.
    with self.assertRaises(InternalServerException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(f'Exception: {message}', context.exception.private_details)
