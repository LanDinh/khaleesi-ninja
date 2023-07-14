"""Test the log metadata."""

# Python.
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import (
  LogRequestMetadata,
  ResponseRequest,
  Response,
  ProcessedResponse,
)
from tests.models import ResponseMetadata


class ResponseMetadataMixinTestCase(SimpleTestCase):
  """Test the log metadata."""

  def testInitialValues(self) -> None :
    """Test initial values."""
    # Execute result.
    instance = ResponseMetadata()
    # Assert result.
    self.assertTrue(instance.inProgress)
    self.assertEqual('IN_PROGRESS', instance.metaResponseStatus)
    self.assertEqual(timedelta(0) , instance.loggedDuration)
    self.assertEqual(timedelta(0) , instance.reportedDuration)
    self.assertEqual(timedelta(0) , instance.metaChildDuration)
    self.assertEqual(0            , instance.childDurationRelative)

  def testInProgress(self) -> None :
    """Test if the request is in progress."""
    # Prepare data.
    instance = ResponseMetadata()
    instance.metaResponseStatus = 'IN_PROGRESS'
    # Execute test.
    result = instance.inProgress
    # Assert result.
    self.assertTrue(result)

  def testNotInProgress(self) -> None :
    """Test if the request is in progress."""
    # Prepare data.
    instance = ResponseMetadata()
    instance.metaResponseStatus = 'NOT_IN_PROGRESS'
    # Execute test.
    result = instance.inProgress
    # Assert result.
    self.assertFalse(result)

  def testReportedDuration(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus = 'NOT_IN_PROGRESS'
    instance.metaResponseReportedTimestamp = now
    instance.metaReportedTimestamp = now - timedelta(hours = 1)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(hours = 1), result)

  def testReportedDurationInProgress(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus = 'IN_PROGRESS'
    instance.metaResponseReportedTimestamp = now
    instance.metaReportedTimestamp = now - timedelta(hours = 1)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(0), result)

  def testLoggedDuration(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus = 'NOT_IN_PROGRESS'
    instance.metaResponseLoggedTimestamp = now
    instance.metaLoggedTimestamp = now - timedelta(hours = 1)
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(hours = 1), result)

  def testLoggedDurationInProgress(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus = 'IN_PROGRESS'
    instance.metaResponseLoggedTimestamp = now
    instance.metaLoggedTimestamp = now - timedelta(hours = 1)
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(0), result)

  def testChildDurationRelative(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'NOT_IN_PROGRESS'
    instance.metaLoggedTimestamp         = now
    instance.metaResponseLoggedTimestamp = now + timedelta(minutes = 10)
    instance.metaChildDuration           = timedelta(minutes = 1)
    # Execute test.
    result = instance.childDurationRelative
    # Assert result.
    self.assertEqual(0.1, result)

  def testChildDurationRelativeInProgress(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'IN_PROGRESS'
    instance.metaLoggedTimestamp         = now
    instance.metaResponseLoggedTimestamp = now + timedelta(minutes = 10)
    instance.metaChildDuration           = timedelta(minutes = 1)
    # Execute test.
    result = instance.childDurationRelative
    # Assert result.
    self.assertEqual(0, result)

  def testChildDurationRelativeNoDivisionByZero(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'NOT_IN_PROGRESS'
    instance.metaLoggedTimestamp         = now
    instance.metaResponseLoggedTimestamp = now
    instance.metaChildDuration           = timedelta(minutes = 1)
    # Execute test.
    result = instance.childDurationRelative
    # Assert result.
    self.assertEqual(0, result)

  @patch('microservice.models.logs.responseMetadataMixin.parseString')
  @patch('microservice.models.logs.responseMetadataMixin.parseTimestamp')
  def testResponseMetadataFromGrpcForCreation(
      self,
      timestamp: MagicMock,
      string   : MagicMock,
  ) -> None :
    """Test logging metadata."""
    # Prepare data.
    now = datetime.now(tz = timezone.utc)
    grpc = self._createResponseRequest(now = now, timestamp = timestamp, string = string)
    initialError = 'test errors'
    instance                    = ResponseMetadata()
    instance.metaResponseStatus = 'NOT_IN_PROGRESS'
    # Execute test.
    instance.responseMetadataFromGrpc(
      metadata = grpc.requestMetadata,
      grpc     = grpc.response,
      errors   = [ initialError ],
    )
    # Assert result.
    self.assertEqual('', instance.metaResponseLoggingErrors)

  @patch('microservice.models.logs.responseMetadataMixin.parseString')
  @patch('microservice.models.logs.responseMetadataMixin.parseTimestamp')
  def testResponseMetadataFromGrpcForUpdateEmpty(
      self,
      timestamp: MagicMock,
      string   : MagicMock,
  ) -> None :
    """Test empty input for logging metadata."""
    # Prepare data.
    timestamp.return_value = None
    string.return_value    = 'parsed-string'
    grpc = ResponseRequest()
    instance                    = ResponseMetadata()
    instance.metaResponseStatus = 'IN_PROGRESS'
    instance._state.adding      = False  # pylint: disable=protected-access
    # Execute test.
    instance.responseMetadataFromGrpc(
      metadata = grpc.requestMetadata,
      grpc     = grpc.response,
      errors   = [ '' ],
    )
    # Assert result.
    self.assertEqual('', instance.metaResponseLoggingErrors)

  @patch('microservice.models.logs.responseMetadataMixin.parseString')
  @patch('microservice.models.logs.responseMetadataMixin.parseTimestamp')
  def testResponseMetadataFromGrpcForUpdate(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    now = datetime.now(tz = timezone.utc)
    grpc = self._createResponseRequest(now = now, timestamp = timestamp, string = string)
    initialError = 'test errors'
    instance                    = ResponseMetadata()
    instance.metaResponseStatus = 'IN_PROGRESS'
    instance._state.adding      = False  # pylint: disable=protected-access
    # Execute test.
    instance.responseMetadataFromGrpc(
      metadata = grpc.requestMetadata,
      grpc     = grpc.response,
      errors   = [ initialError ],
    )
    # Assert result.
    self.assertEqual(initialError, instance.metaResponseLoggingErrors)

  def testMetadataToGrpc(self) -> None :
    """Test transformation to gRPC."""
    # Prepare data.
    now = datetime.now(tz = timezone.utc)
    instance = ResponseMetadata()

    instance.metaResponseStatus            = 'STATUS'
    instance.metaReportedTimestamp         = now
    instance.metaLoggedTimestamp           = now
    instance.metaResponseReportedTimestamp = now
    instance.metaResponseLoggedTimestamp   = now
    instance.metaChildDuration             = timedelta(hours = 13)
    instance.metaResponseLoggingErrors     = 'initial errors'

    response    = Response()
    processed   = ProcessedResponse()
    logMetadata = LogRequestMetadata()

    # Execute test.
    instance.responseMetadataToGrpc(
      logMetadata = logMetadata,
      response    = response,
      processed   = processed,
    )

    # Assert result.
    self.assertEqual(
      instance.metaResponseReportedTimestamp,
      response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(instance.metaResponseStatus, response.status)

    self.assertEqual(instance.loggedDuration       , processed.loggedDuration.ToTimedelta())
    self.assertEqual(instance.reportedDuration     , processed.reportedDuration.ToTimedelta())
    self.assertEqual(instance.metaChildDuration    , processed.childDurationAbsolute.ToTimedelta())
    self.assertEqual(instance.childDurationRelative, processed.childDurationRelative)

    self.assertEqual(instance.metaResponseLoggedTimestamp,
      logMetadata.loggedTimestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(instance.metaResponseLoggingErrors, logMetadata.errors)

  def testMetadataToGrpcEmpty(self) -> None :
    """Test transformation to gRPC."""
    # Prepare data.
    instance = ResponseMetadata()
    response    = Response()
    processed   = ProcessedResponse()
    logMetadata = LogRequestMetadata()
    # Execute test & assert result.
    instance.responseMetadataToGrpc(
      logMetadata = logMetadata,
      response    = response,
      processed   = processed,
    )

  def _createResponseRequest(
      self, *,
      now      : datetime,
      timestamp: MagicMock,
      string   : MagicMock,
  ) -> ResponseRequest :
    """Utility for creating fully populated request metadata objects."""
    timestamp.return_value = now
    string.return_value    = 'parsed-string'
    grpc = ResponseRequest()
    grpc.response.timestamp.FromDatetime(now)
    grpc.response.status = 'status'

    return grpc
