"""Test the core-sawmill lumberjack service."""

# Python.
from datetime import datetime, timezone, timedelta
from typing import Callable, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from microservice.service.lumberjack import (  # type: ignore[attr-defined]
  Service,
  DbEvent,
  DbGrpcRequest,
  DbError,
  DbHttpRequest,
  DbQuery,
)
from tests.models import OldMetadata, Metadata


@patch('microservice.service.lumberjack.LOGGER')
class LumberjackServiceTestCase(SimpleTestCase):
  """Test the core-sawmill lumberjack service."""

  service = Service()

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def testLogEvent(self, serviceRegistry: MagicMock, *_: MagicMock) -> None :
    """Test logging events."""
    self._executeLoggingTests(
      method        = lambda : self.service.LogEvent(MagicMock(), MagicMock()),
      loggingObject = DbEvent.objects,
    )
    serviceRegistry.addService.assert_called()

  def testLogHttpRequest(self, *_: MagicMock) -> None :
    """Test logging requests."""
    self._executeLoggingTests(
      method         = lambda : self.service.LogHttpRequest(MagicMock(), MagicMock()),
      loggingObject  = DbHttpRequest.objects,
      loggingMethod  = 'logRequest',
      expectedResult = OldMetadata(),
    )

  def testLogSystemHttpRequest(self, *_: MagicMock) -> None :
    """Test logging system HTTP requests."""
    self._executeLoggingTests(
      method         = lambda : self.service.LogSystemHttpRequest(MagicMock(), MagicMock()),
      loggingObject  = DbHttpRequest.objects,
      loggingMethod  = 'logSystemRequest',
      expectedResult = OldMetadata(),
    )

  def testLogHttpResponse(self, *_: MagicMock) -> None :
    """Test logging responses."""
    self._executeLoggingTests(
      method         = lambda : self.service.LogHttpRequestResponse(MagicMock(), MagicMock()),
      loggingObject  = DbHttpRequest.objects,
      loggingMethod  = 'logResponse',
      expectedResult = OldMetadata(),
    )

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def testLogGrpcRequest(self, serviceRegistry: MagicMock, *_: MagicMock) -> None :
    """Test logging requests."""
    self._executeLoggingTests(
      method         = lambda : self.service.LogGrpcRequest(MagicMock(), MagicMock()),
      loggingObject  = DbGrpcRequest.objects,
      loggingMethod  = 'logRequest',
      expectedResult = OldMetadata(),
    )
    serviceRegistry.addCall.assert_called()

  def testLogGrpcResponse(self, *_: MagicMock) -> None :
    """Test logging responses."""
    with patch.object(DbGrpcRequest.objects, 'logResponse') as loggingGrpcRequest:
      with patch.object(DbHttpRequest.objects, 'addChildDuration') as loggingHttpRequest:
        with patch.object(DbQuery.objects, 'logQueries') as loggingQuery:
          # Prepare data.
          now = datetime.now().replace(tzinfo = timezone.utc)
          loggingGrpcRequest.return_value = DbGrpcRequest()
          loggingGrpcRequest.return_value.toGrpc = MagicMock()
          loggingGrpcRequest.return_value.save = MagicMock()
          loggingQuery.return_value = [ DbQuery() ]
          loggingQuery.return_value[0].reportedStart = now
          loggingQuery.return_value[0].reportedEnd   = now + timedelta(days = 1)
          # Execute test.
          self.service.LogGrpcResponse(MagicMock(), MagicMock())
          # Assert result.
          loggingHttpRequest.assert_called_once()
          loggingGrpcRequest.assert_called_once()
          loggingQuery.assert_called_once()
          loggingGrpcRequest.return_value.save.assert_called_once_with()

  def testLogError(self, *_: MagicMock) -> None :
    """Test logging events."""
    self._executeLoggingTests(
      method         = lambda : self.service.LogError(MagicMock(), MagicMock()),
      loggingObject  = DbError.objects,
      loggingMethod  = 'logError',
      expectedResult = OldMetadata(),
    )

  def _executeLoggingTests(
      self, *,
      method        : Callable[[], Any],
      loggingObject : Any,
      loggingMethod : str = 'khaleesiCreate',
      expectedResult: Any = Metadata(),
  ) -> None :
    """Execute all typical logging tests."""
    for test in [ self._executeSuccessfulLoggingTest, self._executeLoggingTestWithParsingError ]:
      with self.subTest(test = test.__name__):
        with patch.object(loggingObject, loggingMethod) as logging:
          test(method = method, logging = logging, expectedResult = expectedResult)  # type: ignore[operator]  # pylint: disable=no-value-for-parameter,line-too-long

  def _executeSuccessfulLoggingTest(
      self, *,
      method        : Callable[[], Any],
      logging       : MagicMock,
      expectedResult: Any,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = expectedResult
    # Execute test.
    method()
    # Assert result.
    logging.assert_called_once()

  # noinspection PyUnusedLocal
  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def _executeLoggingTestWithParsingError(
      self,
      _: MagicMock,
      *,
      method        : Callable[[], Any],
      logging       : MagicMock,
      expectedResult: Any,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    expectedResult.metaLoggingErrors = 'some parsing errors'
    logging.return_value = expectedResult
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(expectedResult.metaLoggingErrors, context.exception.privateDetails)
