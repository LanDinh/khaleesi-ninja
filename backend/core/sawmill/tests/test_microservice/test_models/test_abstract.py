"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from typing import List, Tuple, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata as GrpcMetadata, User
from microservice.models.abstract import Metadata


@patch('microservice.models.abstract.parse_timestamp')
class MetadataTestCase(SimpleTestCase):
  """Test the parse utility."""

  def test_log_metadata(self, timestamp: MagicMock) -> None :
    """Test logging metadata."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        timestamp.return_value = (now       , '')
        grpc_metadata = GrpcMetadata()
        grpc_metadata.timestamp.FromDatetime(now)
        grpc_metadata.caller.request_id       = 'request-id'
        grpc_metadata.caller.khaleesi_gate    = 'khaleesi-gate'
        grpc_metadata.caller.khaleesi_service = 'khaleesi-service'
        grpc_metadata.caller.grpc_service     = 'grpc-service'
        grpc_metadata.caller.grpc_method      = 'grpc-method'
        grpc_metadata.user.id                 = 'user-id'
        grpc_metadata.user.type               = user_type
        errors = 'test errors'
        # Execute test.
        result = Metadata.log_metadata(metadata = grpc_metadata, errors = errors)
        # Assert result.
        self.assertEqual(now                                  , result['meta_event_timestamp'])
        self.assertEqual(grpc_metadata.caller.request_id      , result['meta_caller_request_id'])
        self.assertEqual(grpc_metadata.caller.khaleesi_gate   , result['meta_caller_khaleesi_gate'])
        self.assertEqual(
          grpc_metadata.caller.khaleesi_service,
          result['meta_caller_khaleesi_service'],
        )
        self.assertEqual(grpc_metadata.caller.grpc_service    , result['meta_caller_grpc_service'])
        self.assertEqual(grpc_metadata.user.id                , result['meta_user_id'])
        self.assertEqual(user_type                            , result['meta_user_type'])
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

  def test_log_metadata_appends_timezone_errors(self, timestamp: MagicMock) -> None :
    """Test timestamp errors get appended correctly."""
    # Execute test and assert result.
    self._execute_and_assert_append_errors_test(
      errors = [ (datetime.now(tz = timezone.utc), 'invalid event_timestamp') ],
      mock = timestamp,
    )

  def _execute_and_assert_append_errors_test(
      self, *,
      errors: List[Tuple[Any, str]],
      mock  : MagicMock,
  ) -> None :
    # Prepare data.
    initial_error = 'initial_error'
    mock.side_effect = errors
    grpc_metadata = GrpcMetadata()
    # Execute test.
    result = Metadata.log_metadata(metadata = grpc_metadata, errors = initial_error)
    # Assert result.
    self.assertEqual(len(errors), mock.call_count)
    self.assertEqual(1, result['meta_logging_errors'].count(initial_error))
    for _, error in errors:
      self.assertEqual(1, result['meta_logging_errors'].count(error))
