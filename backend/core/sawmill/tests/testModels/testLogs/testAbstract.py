"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata as GrpcMetadata, User
from microservice.models.logs.abstract import Metadata


@patch('microservice.models.logs.abstract.parseString')
@patch('microservice.models.logs.abstract.parseTimestamp')
class MetadataTestCase(SimpleTestCase):
  """Test the parse utility."""

  def testLogMetadata(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test logging metadata."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        timestamp.return_value = now
        string.return_value    = 'parsed-string'
        grpcMetadata = GrpcMetadata()
        grpcMetadata.timestamp.FromDatetime(now)
        grpcMetadata.caller.httpRequestId   = 'http-request-id'
        grpcMetadata.caller.grpcRequestId   = 'grpc-request-id'
        grpcMetadata.caller.khaleesiGate    = 'khaleesi-gate'
        grpcMetadata.caller.khaleesiService = 'khaleesi-service'
        grpcMetadata.caller.grpcService     = 'grpc-service'
        grpcMetadata.caller.grpcMethod      = 'grpc-method'
        grpcMetadata.caller.podId           = 'pod-id'
        grpcMetadata.user.id                = 'user-id'
        grpcMetadata.user.type              = userType
        initialError = 'test errors'
        # Execute test.
        result = Metadata.logMetadata(metadata = grpcMetadata, errors = [ initialError])
        # Assert result.
        self.assertEqual(now         , result['metaReportedTimestamp'])
        self.assertEqual(userType    , result['metaUserType'])
        self.assertEqual(initialError, result['metaLoggingErrors'])

  def testLogMetadataEmpty(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test empty input for logging metadata."""
    # Prepare data.
    timestamp.return_value = None
    string.return_value    = 'parsed-string'
    grpcMetadata           = GrpcMetadata()
    # Execute test.
    result = Metadata.logMetadata(metadata = grpcMetadata, errors = [])
    # Assert result.
    self.assertEqual('', result['metaLoggingErrors'])
