"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata as GrpcMetadata, User
from microservice.models.logs.abstract import Metadata


@patch('microservice.models.logs.abstract.parse_string')
@patch('microservice.models.logs.abstract.parse_timestamp')
class MetadataTestCase(SimpleTestCase):
  """Test the parse utility."""

  def test_log_metadata(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test logging metadata."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        timestamp.return_value = now
        string.return_value    = 'parsed-string'
        grpc_metadata = GrpcMetadata()
        grpc_metadata.timestamp.FromDatetime(now)
        grpc_metadata.caller.httpRequestId   = 'http-request-id'
        grpc_metadata.caller.grpcRequestId   = 'grpc-request-id'
        grpc_metadata.caller.khaleesiGate    = 'khaleesi-gate'
        grpc_metadata.caller.khaleesiService = 'khaleesi-service'
        grpc_metadata.caller.grpcService     = 'grpc-service'
        grpc_metadata.caller.grpcMethod      = 'grpc-method'
        grpc_metadata.caller.podId           = 'pod-id'
        grpc_metadata.user.id                = 'user-id'
        grpc_metadata.user.type              = user_type
        initial_error = 'test errors'
        # Execute test.
        result = Metadata.log_metadata(metadata = grpc_metadata, errors = [ initial_error ])
        # Assert result.
        self.assertEqual(now                            , result['meta_reported_timestamp'])
        self.assertEqual(user_type                      , result['meta_user_type'])
        self.assertEqual(initial_error                  , result['meta_logging_errors'])

  def test_log_metadata_empty(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test empty input for logging metadata."""
    # Prepare data.
    timestamp.return_value = None
    string.return_value    = 'parsed-string'
    grpc_metadata = GrpcMetadata()
    # Execute test.
    result = Metadata.log_metadata(metadata = grpc_metadata, errors = [])
    # Assert result.
    self.assertEqual('', result['meta_logging_errors'])
