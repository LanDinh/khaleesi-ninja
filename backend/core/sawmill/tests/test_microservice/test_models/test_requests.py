"""Test the request logs."""

# Python.
from datetime import datetime, timezone, timedelta
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
        grpc_request.upstream_request.request_id = string.return_value
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
        self.assertTrue(result.is_in_progress)
        self.assertEqual('IN_PROGRESS', result.response_status)
        self.assertEqual(timedelta(0), result.logged_duration)
        self.assertEqual(timedelta(0), result.reported_duration)

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
    self.assertTrue(result.is_in_progress)
    self.assertEqual('IN_PROGRESS', result.response_status)
    self.assertEqual(timedelta(0), result.logged_duration)
    self.assertEqual(timedelta(0), result.reported_duration)

  @patch('microservice.models.request.parse_timestamp')
  @patch.object(Request.objects, 'get')
  def test_log_response(self, request_mock: MagicMock, timestamp: MagicMock) -> None :
    """Test logging a gRPC request response."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        now = datetime.now(tz = timezone.utc) + timedelta(days = 1)
        timestamp.return_value = now
        request_mock.reset_mock()
        request = Request(
          meta_logged_timestamp = datetime.now(tz = timezone.utc),
          meta_reported_timestamp = datetime.now(tz = timezone.utc),
          # Logged timestamps get created at save time, which we mock.
          response_logged_timestamp = datetime.now(tz = timezone.utc) + timedelta(days = 1),
        )
        request.save = MagicMock()  # type: ignore[assignment]
        request_mock.return_value = request
        grpc_response                 = GrpcResponse()
        grpc_response.request_id      = 'request-id'
        grpc_response.response.status = status.name
        grpc_response.response.timestamp.FromDatetime(now)
        # Execute test.
        result = Request.objects.log_response(grpc_response = grpc_response)
        # Assert result.
        result.save.assert_called_once_with()  # type: ignore[attr-defined]
        self.assertEqual(grpc_response.response.status, result.response_status)
        self.assertEqual(
          grpc_response.response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
          result.response_reported_timestamp,
        )
        self.assertFalse(result.is_in_progress)
        self.assertLess(timedelta(0), result.logged_duration)
        self.assertLess(timedelta(0), result.reported_duration)

  @patch('microservice.models.request.parse_timestamp')
  @patch.object(Request.objects, 'get')
  def test_log_empty_response(self, request_mock: MagicMock, timestamp: MagicMock) -> None :
    """Test logging an empty gRPC request response."""
    # Prepare data.
    timestamp.return_value = datetime.min.replace(tzinfo = timezone.utc)
    request_mock.reset_mock()
    request = Request(
      meta_logged_timestamp = datetime.now(tz = timezone.utc),
      meta_reported_timestamp = datetime.now(tz = timezone.utc),
      # Logged timestamps get created at save time, which we mock.
      response_logged_timestamp = datetime.now(tz = timezone.utc) + timedelta(days = 1),
    )
    request.save = MagicMock()  # type: ignore[assignment]
    request_mock.return_value = request
    grpc_response = GrpcResponse()
    # Execute test.
    result = Request.objects.log_response(grpc_response = grpc_response)
    # Assert result.
    result.save.assert_called_once_with()  # type: ignore[attr-defined]
    self.assertIn('response status', result.response_logging_errors)
    self.assertFalse(result.is_in_progress)
    self.assertLess(timedelta(0), result.logged_duration)
    self.assertEqual(timedelta(0), result.reported_duration)


class RequestTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the request logs models."""

  def test_to_grpc_request(self) -> None :
    """Test that general mapping to gRPC works."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        request = Request(
          upstream_request_request_id = '',
          upstream_request_khaleesi_gate = '',
          upstream_request_khaleesi_service = '',
          upstream_request_grpc_service = '',
          upstream_request_grpc_method = '',
          **self.model_full_request_metadata(user = user_type),
          pk = 1337,  # Must be from the DB, so it has a pk. And this needs to match the test data.
          response_status = 'OK',
          response_reported_timestamp = datetime.now(tz = timezone.utc) + timedelta(days = 1),
          response_logged_timestamp = datetime.now(tz = timezone.utc) + timedelta(days = 1),
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
          request.response_reported_timestamp,
          result.response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
        )
        self.assertEqual(
          request.response_logged_timestamp,
          result.response_metadata.logged_timestamp.ToDatetime().replace(tzinfo = timezone.utc),
        )
        self.assertLess(0, result.logged_duration.nanos)
        self.assertLess(0, result.reported_duration.nanos)


  def test_empty_to_grpc_request(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = Request(
      **self.model_empty_request_metadata(),
      pk = 13,  # Must be from the DB, so it has a pk.
      # We provide default values, so they exist.
      response_reported_timestamp = datetime.now(tz = timezone.utc) + timedelta(days = 1),
      response_logged_timestamp = datetime.now(tz = timezone.utc) + timedelta(days = 1),
    )
    # Execute test.
    result = request.to_grpc_request_response()
    # Assert result.
    self.assertIsNotNone(result)
    self.assertEqual(0, result.logged_duration.nanos)
    self.assertEqual(0, result.reported_duration.nanos)
