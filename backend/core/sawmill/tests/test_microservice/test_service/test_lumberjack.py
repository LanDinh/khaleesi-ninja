"""Test the core-sawmill lumberjack service."""

# Python.
from functools import partial
from typing import Callable, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.exceptions import InvalidArgumentException, InternalServerException
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.models.abstract import Metadata as AbstractMetadata
from microservice.service.lumberjack import (  # type: ignore[attr-defined]
    Service,
    DbEvent, DbRequest,
)
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

  def test_log_request(self) -> None :
    """Test logging events."""
    self._execute_logging_tests(
      method = lambda : self.service.LogRequest(MagicMock(), MagicMock()),
      logging_object = DbRequest.objects,
      logging_method = 'log_request',
      return_value = partial(Metadata, pk = 13),
    )

  def _execute_logging_tests(
      self, *,
      method: Callable[[], Any],
      logging_object: Any,
      logging_method: str,
      return_value: Callable[[], AbstractMetadata] = Metadata,
  ) -> None :
    """Execute all typical logging tests."""
    for test in [
        self._execute_successful_logging_test,
        self._execute_logging_test_with_parsing_error,
        self._execute_logging_test_with_fatal_error
    ]:
      with self.subTest(test = test.__name__):
        with patch.object(logging_object, logging_method) as logging:
          test(method = method, logging = logging,  return_value = return_value)

  def _execute_successful_logging_test(
      self, *,
      method: Callable[[], Any],
      logging: MagicMock,
      return_value: Callable[[], AbstractMetadata],
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = return_value()
    # Execute test.
    method()
    # Assert result.
    logging.assert_called_once()

  # noinspection PyUnusedLocal
  def _execute_logging_test_with_parsing_error(
      self, *,
      method: Callable[[], Any],
      logging: MagicMock,
      return_value: Callable[[], AbstractMetadata],
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    expected_result = return_value()
    expected_result.meta_logging_errors = 'some parsing errors'
    logging.return_value = expected_result
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(expected_result.meta_logging_errors, context.exception.private_details)

  # noinspection PyUnusedLocal
  def _execute_logging_test_with_fatal_error(
      self, *,
      method: Callable[[], Any],
      logging: MagicMock,
      return_value: Callable[[], AbstractMetadata],  # pylint: disable=unused-argument
  ) -> None :
    """Call to logging method that results in fatal errors."""
    # Prepare data.
    message = 'fatal exception'
    logging.side_effect = Exception(message)
    # Execute test & assert result.
    with self.assertRaises(InternalServerException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(f'Exception: {message}', context.exception.private_details)
