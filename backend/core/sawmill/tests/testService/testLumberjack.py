"""Test the core-sawmill lumberjack service."""

# Python.
from typing import Callable, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from microservice.service.lumberjack import Service


@patch('microservice.service.lumberjack.LOGGER')
class LumberjackServiceTestCase(SimpleTestCase):
  """Test the core-sawmill lumberjack service."""

  service = Service()

  def testLogHttpRequest(self, *_: MagicMock) -> None :
    """Test logging requests."""
    self._executeLoggingTests(
      method        = lambda : self.service.LogHttpRequest(MagicMock(), MagicMock()),
      loggingObject = 'sendLogHttpRequest',
    )

  def testLogHttpResponse(self, *_: MagicMock) -> None :
    """Test logging responses."""
    self._executeResponseLoggingTests(
      method        = lambda : self.service.LogHttpRequestResponse(MagicMock(), MagicMock()),
      loggingObject = 'sendLogHttpResponse',
    )

  def testLogGrpcRequest(self, *_: MagicMock) -> None :
    """Test logging requests."""
    self._executeLoggingTests(
      method         = lambda : self.service.LogGrpcRequest(MagicMock(), MagicMock()),
      loggingObject  = 'sendLogGrpcRequest',
    )

  def testLogGrpcResponse(self, *_: MagicMock) -> None :
    """Test logging responses."""
    self._executeResponseLoggingTests(
      method        = lambda : self.service.LogGrpcResponse(MagicMock(), MagicMock()),
      loggingObject = 'sendLogGrpcResponse',
    )

  @patch('microservice.service.lumberjack.SITE_REGISTRY')
  def testLogEvent(self, siteRegistry: MagicMock, *_: MagicMock) -> None :
    """Test logging events."""
    self._executeLoggingTests(
      method        = lambda : self.service.LogEvent(MagicMock(), MagicMock()),
      loggingObject = 'sendLogEvent',
    )
    siteRegistry.addService.assert_called()

  def testLogError(self, *_: MagicMock) -> None :
    """Test logging events."""
    self._executeLoggingTests(
      method        = lambda : self.service.LogError(MagicMock(), MagicMock()),
      loggingObject = 'sendLogError',
    )

  def _executeLoggingTests(self, *, method: Callable[[], Any], loggingObject: str) -> None :
    """Execute all typical logging tests."""
    for test in [ self._executeSuccessfulLoggingTest, self._executeLoggingTestWithParsingError ]:
      with self.subTest(test = test.__name__):
        with patch(f'microservice.service.lumberjack.SINGLETON.structuredLogger.{loggingObject}') \
            as logging:
          test(method = method, logging = logging)  # type: ignore[operator]  # pylint: disable=line-too-long

  def _executeResponseLoggingTests(self, *, method: Callable[[], Any], loggingObject: str) -> None :
    """Execute all typical logging tests."""
    for test in [
        self._executeSuccessfulResponseLoggingTest,
        self._executeResponseLoggingTestWithParsingError,
    ]:
      with self.subTest(test = test.__name__):
        with patch(f'microservice.service.lumberjack.SINGLETON.structuredLogger.{loggingObject}') \
            as logging:
          test(method = method, logging = logging)  # type: ignore[operator]  # pylint: disable=line-too-long


  def _executeSuccessfulLoggingTest(
      self, *,
      method : Callable[[], Any],
      logging: MagicMock,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaLoggingErrors = ''
    # Execute test.
    method()
    # Assert result.
    logging.assert_called_once()
    logging.return_value.toObjectMetadata.assert_called_once()

  # noinspection PyUnusedLocal
  @patch('microservice.service.lumberjack.SITE_REGISTRY')
  def _executeLoggingTestWithParsingError(
      self,
      _: MagicMock,
      *,
      method : Callable[[], Any],
      logging: MagicMock,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaResponseLoggingErrors = 'some parsing errors'
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(logging.return_value.metaLoggingErrors, context.exception.privateDetails)

  def _executeSuccessfulResponseLoggingTest(
      self, *,
      method : Callable[[], Any],
      logging: MagicMock,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaResponseLoggingErrors = ''
    # Execute test.
    method()
    # Assert result.
    logging.assert_called_once()
    logging.return_value.toObjectMetadata.assert_called_once()

  # noinspection PyUnusedLocal
  @patch('microservice.service.lumberjack.SITE_REGISTRY')
  def _executeResponseLoggingTestWithParsingError(
      self,
      _: MagicMock,
      *,
      method : Callable[[], Any],
      logging: MagicMock,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaResponseLoggingErrors = 'some parsing errors'
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(
      logging.return_value.metaResponseLoggingErrors,
      context.exception.privateDetails,
    )
