"""Test the core-sawmill lumberjack service."""

# Python.
from functools import partial
from typing import Callable, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.models.abstract import Metadata as AbstractMetadata
from microservice.service.lumberjack import (  # type: ignore[attr-defined]
  Service,
  DbEvent,
  DbRequest,
  DbError,
)
from tests.models import Metadata


@patch('microservice.service.lumberjack.LOGGER')
class LumberjackServiceTestCase(SimpleTestCase):
  """Test the core-sawmill lumberjack service."""

  service = Service()

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def test_log_event(self, service_registry: MagicMock) -> None :
    """Test logging events."""
    self._execute_logging_tests(
      method = lambda : self.service.LogEvent(MagicMock(), MagicMock()),
      logging_object = DbEvent.objects,
      logging_method = 'log_event',
    )
    service_registry.add_service.assert_called()

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def test_log_request(self, service_registry: MagicMock) -> None :
    """Test logging requests."""
    self._execute_logging_tests(
      method = lambda : self.service.LogRequest(MagicMock(), MagicMock()),
      logging_object = DbRequest.objects,
      logging_method = 'log_request',
      return_value = partial(Metadata, pk = 13),
    )
    service_registry.add_call.assert_called()

  def test_log_response(self) -> None :
    """Test logging responses."""
    self._execute_logging_tests(
      method = lambda : self.service.LogResponse(MagicMock(), MagicMock()),
      logging_object = DbRequest.objects,
      logging_method = 'log_response',
    )

  def test_log_error(self) -> None :
    """Test logging events."""
    self._execute_logging_tests(
      method = lambda : self.service.LogError(MagicMock(), MagicMock()),
      logging_object = DbError.objects,
      logging_method = 'log_error',
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
    ]:
      with self.subTest(test = test.__name__):
        with patch.object(logging_object, logging_method) as logging:
          test(method = method, logging = logging,  return_value = return_value)  # type: ignore[operator]  # pylint: disable=no-value-for-parameter,line-too-long

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
  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def _execute_logging_test_with_parsing_error(
      self,
      _: MagicMock,
      *,
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
