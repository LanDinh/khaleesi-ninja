"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata as GrpcMetadata, User
from microservice.models.abstract import Metadata


@patch('microservice.models.abstract.parse_string')
@patch('microservice.models.abstract.parse_timestamp')
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
        grpc_metadata.caller.request_id       = 'request-id'
        grpc_metadata.caller.khaleesi_gate    = 'khaleesi-gate'
        grpc_metadata.caller.khaleesi_service = 'khaleesi-service'
        grpc_metadata.caller.grpc_service     = 'grpc-service'
        grpc_metadata.caller.grpc_method      = 'grpc-method'
        grpc_metadata.user.id                 = 'user-id'
        grpc_metadata.user.type               = user_type
        initial_error = 'test errors'
        # Execute test.
        result = Metadata.log_metadata(metadata = grpc_metadata, errors = [ initial_error ])
        # Assert result.
        self.assertEqual(now                            , result['meta_event_timestamp'])
        self.assertEqual(grpc_metadata.caller.request_id, result['meta_caller_request_id'])
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
