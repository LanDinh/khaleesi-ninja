"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import LoggingMetadata as GrpcMetadata
from microservice.models.abstract import Metadata


@patch('microservice.models.abstract.parse_timestamp')
class MetadataTestCase(SimpleTestCase):
  """Test the parse utility."""

  def test_log_metadata(self, timestamp: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    now = datetime.now(tz = timezone.utc)
    timestamp.return_value = (now, '')
    grpc_metadata = GrpcMetadata()
    grpc_metadata.timestamp.FromDatetime(now)
    grpc_metadata.logger.request_id       = 'request-id'
    grpc_metadata.logger.khaleesi_gate    = 'khaleesi-gate'
    grpc_metadata.logger.khaleesi_service = 'khaleesi-service'
    grpc_metadata.logger.grpc_service     = 'grpc-service'
    grpc_metadata.logger.grpc_method      = 'grpc-method'
    errors = 'test errors'
    # Execute test.
    result = Metadata.log_metadata(metadata = grpc_metadata, errors = errors)
    # Assert result.
    self.assertEqual(now                                  , result['meta_event_timestamp'])
    self.assertEqual(grpc_metadata.logger.request_id      , result['meta_logger_request_id'])
    self.assertEqual(grpc_metadata.logger.khaleesi_gate   , result['meta_logger_khaleesi_gate'])
    self.assertEqual(grpc_metadata.logger.khaleesi_service, result['meta_logger_khaleesi_service'])
    self.assertEqual(grpc_metadata.logger.grpc_service    , result['meta_logger_grpc_service'])
    self.assertEqual(grpc_metadata.logger.grpc_method     , result['meta_logger_grpc_method'])
    self.assertEqual(errors                               , result['meta_logging_errors'])

  def test_log_metadata_empty(self, timestamp: MagicMock) -> None :
    """Test empty input for logging metadata."""
    # Prepare data.
    timestamp.return_value = (None, '')
    grpc_metadata = GrpcMetadata()
    errors = ''
    # Execute test.
    result = Metadata.log_metadata(metadata = grpc_metadata, errors = errors)
    # Assert result.
    self.assertEqual(errors, result['meta_logging_errors'])

  def test_log_metadata_appends_uuid_errors(self, timestamp: MagicMock) -> None :
    """Test timestamp errors get appended correctly."""
    # Prepare data.
    initial_error = 'initial_error'
    errors = [ (datetime.now(tz = timezone.utc), 'invalid event_timestamp') ]
    timestamp.side_effect = errors
    grpc_metadata = GrpcMetadata()
    # Execute test.
    result = Metadata.log_metadata(metadata = grpc_metadata, errors = initial_error)
    # Assert result.
    self.assertEqual(len(errors), timestamp.call_count)
    self.assertEqual(1, result['meta_logging_errors'].count(initial_error))
    for _, error in errors:
      self.assertEqual(1, result['meta_logging_errors'].count(error))
