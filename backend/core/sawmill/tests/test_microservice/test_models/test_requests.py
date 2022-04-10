"""Test the request logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Request as GrpcRequest
from microservice.models import Request
from microservice.test_util import ModelRequestMetadataMixin


@patch('microservice.models.event.parse_string')
@patch.object(Request.objects.model, 'log_metadata')
class RequestManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the request logs objects manager."""

  def test_log_request(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging a gRPC request."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        metadata.reset_mock()
        metadata.return_value = {}
        string.return_value = 'parsed-string'
        now = datetime.now(tz = timezone.utc)
        grpc_request = GrpcRequest()
        self.set_request_metadata(
          request_metadata = grpc_request.request_metadata,
          now = now,
          user = user_type,
        )
        grpc_request.upstream_request.request_id = 13
        grpc_request.upstream_request.khaleesi_gate = 'upstream-khaleesi-gate'
        grpc_request.upstream_request.khaleesi_service = 'upstream-khaleesi-service'
        grpc_request.upstream_request.grpc_service = 'upstream-grpc-service'
        grpc_request.upstream_request.grpc_method = 'upstream-grpc-method'
        # Execute test.
        result = Request.objects.log_request(grpc_request = grpc_request)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpc_request.request_metadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                           , metadata.call_args.kwargs['errors'])
        self.assertEqual(
          grpc_request.upstream_request.request_id,
          result.upstream_request_request_id,
        )
        self.assertEqual(
          grpc_request.upstream_request.khaleesi_gate,
          result.upstream_request_khaleesi_gate,
        )
        self.assertEqual(
          grpc_request.upstream_request.khaleesi_service,
          result.upstream_request_khaleesi_service,
        )
        self.assertEqual(
          grpc_request.upstream_request.grpc_service,
          result.upstream_request_grpc_service,
        )
        self.assertEqual(
          grpc_request.upstream_request.grpc_method,
          result.upstream_request_grpc_method,
        )

  def test_log_request_empty(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging an empty gRPC request."""
    # Prepare data.
    string.return_value = 'parsed-string'
    metadata.return_value = {}
    grpc_request = GrpcRequest()
    # Execute test.
    result = Request.objects.log_request(grpc_request = grpc_request)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)


class RequestTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the request logs models."""

  def test_to_grpc_request(self) -> None :
    """Test that general mapping to gRPC works."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        request = Request(
          upstream_request_request_id = 13,
          upstream_request_khaleesi_gate = '',
          upstream_request_khaleesi_service = '',
          upstream_request_grpc_service = '',
          upstream_request_grpc_method = '',
          **self.model_full_request_metadata(user = user_type),
        )
        # Execute test.
        result = request.to_grpc_request_response()
        # Assert result.
        self.assert_grpc_request_metadata(
          model = request,
          grpc = result.request.request_metadata,
          grpc_response = result.request_metadata,
        )
        self.assertEqual(
          request.upstream_request_request_id,
          result.request.upstream_request.request_id,
        )
        self.assertEqual(
          request.upstream_request_khaleesi_gate,
          result.request.upstream_request.khaleesi_gate,
        )
        self.assertEqual(
          request.upstream_request_khaleesi_service,
          result.request.upstream_request.khaleesi_service,
        )
        self.assertEqual(
          request.upstream_request_grpc_service,
          result.request.upstream_request.grpc_service,
        )
        self.assertEqual(
          request.upstream_request_grpc_method,
          result.request.upstream_request.grpc_method,
        )

  def test_empty_to_grpc_request(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    event = Request(**self.model_empty_request_metadata())
    # Execute test.
    result = event.to_grpc_request_response()
    # Assert result.
    self.assertIsNotNone(result)
