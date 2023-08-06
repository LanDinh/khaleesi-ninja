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
from microservice.models.logs.metadataMixin import MIN_TIMESTAMP
from tests.models import ResponseMetadata


class ResponseMetadataMixinTestCase(SimpleTestCase):  # pylint: disable=too-many-public-methods
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
    """Test reported duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus            = 'NOT_IN_PROGRESS'
    instance.metaResponseReportedTimestamp = now
    instance.metaReportedTimestamp         = now - timedelta(hours = 1)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(hours = 1), result)

  def testReportedDurationInProgress(self) -> None :
    """Test reported duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus            = 'IN_PROGRESS'
    instance.metaResponseReportedTimestamp = now
    instance.metaReportedTimestamp         = now - timedelta(hours = 1)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(0), result)

  def testReportedDurationEmptyStart(self) -> None :
    """Test reported duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus            = 'NOT_IN_PROGRESS'
    instance.metaResponseReportedTimestamp = now
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testReportedDurationEmptyEnd(self) -> None :
    """Test reported duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus    = 'NOT_IN_PROGRESS'
    instance.metaReportedTimestamp = now
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testReportedDurationMinEnd(self) -> None :
    """Test reported duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus            = 'NOT_IN_PROGRESS'
    instance.metaResponseReportedTimestamp = MIN_TIMESTAMP
    instance.metaReportedTimestamp         = now - timedelta(hours = 1)
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testReportedDurationMinStart(self) -> None :
    """Test reported duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus            = 'NOT_IN_PROGRESS'
    instance.metaResponseReportedTimestamp = now
    instance.metaReportedTimestamp         = MIN_TIMESTAMP
    # Execute test.
    result = instance.reportedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testLoggedDuration(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'NOT_IN_PROGRESS'
    instance.metaResponseLoggedTimestamp = now
    instance.metaLoggedTimestamp         = now - timedelta(hours = 1)
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(hours = 1), result)

  def testLoggedDurationInProgress(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'IN_PROGRESS'
    instance.metaResponseLoggedTimestamp = now
    instance.metaLoggedTimestamp         = now - timedelta(hours = 1)
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(0), result)

  def testLoggedDurationEmptyStart(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'NOT_IN_PROGRESS'
    instance.metaResponseLoggedTimestamp = now
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testLoggedDurationEmptyEnd(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus  = 'NOT_IN_PROGRESS'
    instance.metaLoggedTimestamp = now - timedelta(hours = 1)
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testLoggedDurationMinStart(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'NOT_IN_PROGRESS'
    instance.metaResponseLoggedTimestamp = now
    instance.metaLoggedTimestamp         = MIN_TIMESTAMP
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

  def testLoggedDurationMinEnd(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    instance = ResponseMetadata()
    instance.metaResponseStatus          = 'NOT_IN_PROGRESS'
    instance.metaResponseLoggedTimestamp = MIN_TIMESTAMP
    instance.metaLoggedTimestamp         = now - timedelta(hours = 1)
    # Execute test.
    result = instance.loggedDuration
    # Assert result.
    self.assertEqual(timedelta(), result)

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

  def testAddChildDuration(self) -> None :
    """Test adding child durations."""
    # Prepare data.
    initialDuration = timedelta(hours = 1)
    addedDuration = timedelta(hours = 13)
    instance = ResponseMetadata()
    instance.metaChildDuration = initialDuration
    # Execute test.
    instance.addChildDuration(duration = addedDuration)
    # Assert result.
    self.assertEqual(addedDuration + initialDuration, instance.metaChildDuration)

  @patch('tests.models.ResponseMetadata.toGrpc')
  @patch('tests.models.ResponseMetadata.khaleesiSave')
  def testFinish(self, parent: MagicMock, toGrpc: MagicMock) -> None :
    """Test logging a gRPC HTTP request response."""
    # Prepare data.
    instance = ResponseMetadata()
    # Execute test.
    instance.finish(request = MagicMock())
    # Assert result.
    parent.assert_called_once()
    toGrpc.assert_called_once()

  @patch('microservice.models.logs.responseMetadataMixin.parseString')
  def testResponseMetadataFromGrpcForCreation(self, string: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    grpc = self._createResponseRequest(string = string)
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
  def testResponseMetadataFromGrpcForUpdate(self, string: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    grpc = self._createResponseRequest(string = string)
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

  def testToObjectMetadata(self) -> None :
    """Test the signature is there."""
    # Prepare data.
    instance = ResponseMetadata()
    # Execute test & assert result.
    instance.toObjectMetadata()

  def _createResponseRequest(self, *, string: MagicMock) -> ResponseRequest :
    """Utility for creating fully populated request metadata objects."""
    string.return_value    = 'parsed-string'
    grpc = ResponseRequest()
    grpc.response.status = 'status'

    return grpc
