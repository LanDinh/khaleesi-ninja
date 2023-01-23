"""Test the error logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LogLevel
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Error as GrpcError
from microservice.models import Error
from microservice.test_util import ModelRequestMetadataMixin


@patch('microservice.models.logs.event.parse_string')
@patch.object(Error.objects.model, 'log_metadata')
class ErrorManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the error logs objects manager."""

  def test_cleanup(self, *_: MagicMock) -> None :
    """Test cleanup."""
    # Execute test.
    Error.objects.cleanup.__wrapped__(MagicMock(), MagicMock())  # type: ignore[attr-defined]  # pylint: disable=no-member

  def test_log_error(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging an error."""
    for status in StatusCode:
      for loglevel in LogLevel:
        for user_label, user_type in User.UserType.items():
          with self.subTest(status = status.name, loglevel = loglevel.name, user = user_label):
            # Prepare data.
            metadata.reset_mock()
            metadata.return_value = {}
            string.return_value = 'parsed-string'
            now = datetime.now(tz = timezone.utc)
            grpc_error = GrpcError()
            self.set_request_metadata(
              request_metadata = grpc_error.request_metadata,
              now = now,
              user = user_type,
            )
            grpc_error.id              = 'error-id'
            grpc_error.status          = status.name
            grpc_error.loglevel        = loglevel.name
            grpc_error.gate            = 'gate'
            grpc_error.service         = 'service'
            grpc_error.public_key      = 'public-key'
            grpc_error.public_details  = 'public-details'
            grpc_error.private_message = 'private-message'
            grpc_error.private_details = 'private-details'
            grpc_error.stacktrace      = 'stacktrace'
            # Execute test.
            result = Error.objects.log_error(grpc_error = grpc_error)
            # Assert result.
            metadata.assert_called_once()
            self.assertEqual(grpc_error.request_metadata, metadata.call_args.kwargs['metadata'])
            self.assertEqual([]                         , metadata.call_args.kwargs['errors'])
            self.assertEqual(grpc_error.public_details  , result.public_details)
            self.assertEqual(grpc_error.private_message , result.private_message)
            self.assertEqual(grpc_error.private_details , result.private_details)
            self.assertEqual(grpc_error.stacktrace      , result.stacktrace)

  def test_log_error_empty(
      self,
      metadata: MagicMock,
      string: MagicMock,
  ) -> None :
    """Test logging an empty error."""
    # Prepare data.
    string.return_value = 'parsed-string'
    metadata.return_value = {}
    grpc_error = GrpcError()
    # Execute test.
    result = Error.objects.log_error(grpc_error = grpc_error)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)


class ErrorTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the error logs models."""

  def test_to_grpc_error(self) -> None :
    """Test that general mapping to gRPC works."""
    for status in StatusCode:
      for loglevel in LogLevel:
        for user_label, user_type in User.UserType.items():
          with self.subTest(status = status.name, user = user_label):
            # Prepare data.
            error = Error(
              error_id        = 'error-id',
              status          = status.name,
              loglevel        = loglevel.name,
              gate            = 'gate',
              service         = 'service',
              public_key      = 'public-key',
              public_details  = 'public-details',
              private_message = 'private_message',
              private_details = 'private_details',
              stacktrace      = 'stacktrace',
              **self.model_full_request_metadata(user = user_type),
            )
            # Execute test.
            result = error.to_grpc_error_response()
            # Assert result.
            self.assert_grpc_request_metadata(
              model = error,
              grpc = result.error.request_metadata,
              grpc_response = result.error_metadata,
            )
            self.assertEqual(error.error_id             , result.error.id)
            self.assertEqual(error.status         , result.error.status)
            self.assertEqual(error.loglevel       , result.error.loglevel)
            self.assertEqual(error.gate           , result.error.gate)
            self.assertEqual(error.service        , result.error.service)
            self.assertEqual(error.public_key     , result.error.public_key)
            self.assertEqual(error.public_details , result.error.public_details)
            self.assertEqual(error.private_message, result.error.private_message)
            self.assertEqual(error.private_details, result.error.private_details)
            self.assertEqual(error.stacktrace     , result.error.stacktrace)

  def test_empty_to_grpc_error(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    error = Error(**self.model_empty_request_metadata())
    # Execute test.
    result = error.to_grpc_error_response()
    # Assert result.
    self.assertIsNotNone(result)
