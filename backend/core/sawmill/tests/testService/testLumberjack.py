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
  DbGrpcRequest,
  DbHttpRequest,
  DbQuery,
)


@patch('microservice.service.lumberjack.LOGGER')
class LumberjackServiceTestCase(SimpleTestCase):
  """Test the core-sawmill lumberjack service."""

  service = Service()

  def testLogHttpRequest(self, *_: MagicMock) -> None :
    """Test logging requests."""
    self._executeLoggingTests(
      method        = lambda : self.service.LogHttpRequest(MagicMock(), MagicMock()),
      loggingObject = 'DbHttpRequest',
    )

  def testLogHttpResponse(self, *_: MagicMock) -> None :
    """Test logging responses."""
    self._executeResponseLoggingTests(
      method        = lambda : self.service.LogHttpRequestResponse(MagicMock(), MagicMock()),
      loggingObject = 'DbHttpRequest',
    )

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def testLogEvent(self, serviceRegistry: MagicMock, *_: MagicMock) -> None :
    """Test logging events."""
    self._executeLoggingTests(
      method        = lambda : self.service.LogEvent(MagicMock(), MagicMock()),
      loggingObject = 'DbEvent',
    )
    serviceRegistry.addService.assert_called()

  def testLogError(self, *_: MagicMock) -> None :
    """Test logging events."""
    self._executeLoggingTests(
      method        = lambda : self.service.LogError(MagicMock(), MagicMock()),
      loggingObject = 'DbError',
    )

  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def testLogGrpcRequest(self, serviceRegistry: MagicMock, *_: MagicMock) -> None :
    """Test logging requests."""
    self._executeOldLoggingTests(
      method         = lambda : self.service.LogGrpcRequest(MagicMock(), MagicMock()),
      loggingObject  = DbGrpcRequest.objects,
      loggingMethod  = 'logRequest',
    )
    serviceRegistry.addCall.assert_called()

  def testLogGrpcResponse(self, *_: MagicMock) -> None :
    """Test logging responses."""
    with patch.object(DbGrpcRequest.objects, 'logResponse') as loggingGrpcRequest:
      with patch.object(DbHttpRequest.objects, 'get') as loggingHttpRequest:
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
          loggingHttpRequest.return_value.addChildDuration.assert_called_once()
          loggingGrpcRequest.assert_called_once()
          loggingQuery.assert_called_once()
          loggingGrpcRequest.return_value.save.assert_called_once_with()

  def _executeLoggingTests(
      self, *,
      method        : Callable[[], Any],
      loggingObject : str,
  ) -> None :
    """Execute all typical logging tests."""
    for test in [ self._executeSuccessfulLoggingTest, self._executeLoggingTestWithParsingError ]:
      with self.subTest(test = test.__name__):
        with patch(f'microservice.service.lumberjack.{loggingObject}') as logging:
          test(method = method, logging = logging)  # type: ignore[operator]  # pylint: disable=line-too-long

  def _executeResponseLoggingTests(
      self, *,
      method        : Callable[[], Any],
      loggingObject : str,
  ) -> None :
    """Execute all typical logging tests."""
    for test in [
        self._executeSuccessfulResponseLoggingTest,
        self._executeResponseLoggingTestWithParsingError,
    ]:
      with self.subTest(test = test.__name__):
        with patch(f'microservice.service.lumberjack.{loggingObject}') as logging:
          test(method = method, logging = logging)  # type: ignore[operator]  # pylint: disable=line-too-long


  def _executeOldLoggingTests(
      self, *,
      method        : Callable[[], Any],
      loggingObject : Any,
      loggingMethod : str,
  ) -> None :
    """Execute all typical logging tests."""
    for test in [
        self._executeOldSuccessfulLoggingTest,
        self._executeOldLoggingTestWithParsingError,
    ]:
      with self.subTest(test = test.__name__):
        with patch.object(loggingObject, loggingMethod) as logging:
          test(method = method, logging = logging)  # type: ignore[operator]  # pylint: disable=no-value-for-parameter,line-too-long

  def _executeSuccessfulLoggingTest(
      self, *,
      method      : Callable[[], Any],
      logging     : MagicMock,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaLoggingErrors = ''
    # Execute test.
    method()
    # Assert result.
    logging.return_value.khaleesiSave.assert_called_once()
    logging.return_value.toObjectMetadata.assert_called_once()

  # noinspection PyUnusedLocal
  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def _executeLoggingTestWithParsingError(
      self,
      _: MagicMock,
      *,
      method      : Callable[[], Any],
      logging     : MagicMock,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaResponseLoggingErrors = 'some parsing errors'
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.return_value.khaleesiSave.assert_called_once()
    self.assertEqual(logging.return_value.metaLoggingErrors, context.exception.privateDetails)

  def _executeSuccessfulResponseLoggingTest(
      self, *,
      method      : Callable[[], Any],
      logging     : MagicMock,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.objects.get.return_value = MagicMock()
    logging.objects.get.return_value.metaResponseLoggingErrors = ''
    # Execute test.
    method()
    # Assert result.
    logging.objects.get.return_value.finish.assert_called_once()
    logging.objects.get.return_value.toObjectMetadata.assert_called_once()

  # noinspection PyUnusedLocal
  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def _executeResponseLoggingTestWithParsingError(
      self,
      _: MagicMock,
      *,
      method      : Callable[[], Any],
      logging     : MagicMock,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    logging.objects.get.return_value = MagicMock()
    logging.objects.get.return_value.metaResponseLoggingErrors = 'some parsing errors'
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.objects.get.return_value.finish.assert_called_once()
    self.assertEqual(
      logging.objects.get.return_value.metaResponseLoggingErrors,
      context.exception.privateDetails,
    )

  def _executeOldSuccessfulLoggingTest(
      self, *,
      method        : Callable[[], Any],
      logging       : MagicMock,
  ) -> None :
    """Successful call to logging method."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaLoggingErrors = ''
    # Execute test.
    method()
    # Assert result.
    logging.assert_called_once()

  # noinspection PyUnusedLocal
  @patch('microservice.service.lumberjack.SERVICE_REGISTRY')
  def _executeOldLoggingTestWithParsingError(
      self,
      _: MagicMock,
      *,
      method        : Callable[[], Any],
      logging       : MagicMock,
  ) -> None :
    """Call to logging method that results in parsing errors."""
    # Prepare data.
    logging.return_value = MagicMock()
    logging.return_value.metaLoggingErrors = 'some parsing errors'
    # Execute test & assert result.
    with self.assertRaises(InvalidArgumentException) as context:
      method()
    logging.assert_called_once()
    self.assertEqual(logging.return_value.metaLoggingErrors, context.exception.privateDetails)
