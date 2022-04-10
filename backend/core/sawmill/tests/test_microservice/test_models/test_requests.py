"""Test the request logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Request as GrpcRequest, ResponseRequest as GrpcResponse
from microservice.models import Request
from microservice.test_util import ModelRequestMetadataMixin


class RequestManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the request logs objects manager."""

  @patch('microservice.models.request.parse_string')
  @patch.object(Request.objects.model, 'log_metadata')
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
        grpc_request.upstream_request.khaleesi_gate = string.return_value
        grpc_request.upstream_request.khaleesi_service = string.return_value
        grpc_request.upstream_request.grpc_service = string.return_value
        grpc_request.upstream_request.grpc_method = string.return_value
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

  @patch('microservice.models.event.parse_string')
  @patch.object(Request.objects.model, 'log_metadata')
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

  @patch('microservice.models.request.parse_timestamp')
  @patch.object(Request.objects, 'get')
  def test_log_response(self, _: MagicMock, timestamp: MagicMock) -> None :
    """Test logging a gRPC request response."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        timestamp.return_value = now
        grpc_response = GrpcResponse()
        grpc_response.request_id = 13
        grpc_response.response.status = 1337
        grpc_response.response.timestamp.FromDatetime(now)
        # Execute test.
        result = Request.objects.log_response(grpc_response = grpc_response)
        # Assert result.
        result.save.assert_called_once_with()  # type: ignore[attr-defined]
        result.reset_mock()  # type: ignore[attr-defined]
        self.assertEqual(grpc_response.response.status,    result.response_status)
        self.assertEqual(
          grpc_response.response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
          result.response_event_timestamp,
        )

  @patch('microservice.models.request.parse_timestamp')
  @patch.object(Request.objects, 'get')
  def test_log_empty_response(self, *_: MagicMock) -> None :
    """Test logging an empty gRPC request response."""
    # Prepare data.
    grpc_response = GrpcResponse()
    # Execute test.
    result = Request.objects.log_response(grpc_response = grpc_response)
    # Assert result.
    result.save.assert_called_once_with()  # type: ignore[attr-defined]
    result.reset_mock()  # type: ignore[attr-defined]
    self.assertIn('response status', result.response_logging_errors)


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
          pk = 1337,  # Must be from the DB, so it has a pk. And this needs to match the test data.
          response_status = 42,
          response_event_timestamp = datetime.now(tz = timezone.utc),
          response_logged_timestamp = datetime.now(tz = timezone.utc),
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
        self.assertEqual(
          request.response_status,
          result.response.status,
        )
        self.assertEqual(
          request.response_event_timestamp,
          result.response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
        )
        self.assertEqual(
          request.response_logged_timestamp,
          result.response_metadata.logged_timestamp.ToDatetime().replace(tzinfo = timezone.utc),
        )


  def test_empty_to_grpc_request(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = Request(
      **self.model_empty_request_metadata(),
      pk = 13,  # Must be from the DB, so it has a pk.
      # We provide default values, so they exist.
      response_event_timestamp = datetime.now(tz = timezone.utc),
      response_logged_timestamp = datetime.now(tz = timezone.utc),
    )
    # Execute test.
    result = request.to_grpc_request_response()
    # Assert result.
    self.assertIsNotNone(result)
