"""Test the request logs."""

# Python.
from datetime import timezone, timedelta, datetime
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import (
  Response as GrpcResponse,
  RequestResponse as GrpcRequestResponse,
)
from microservice.test_util import ModelResponseMetadataMixin
from tests.models import ResponseMetadata


class ResponseMetadataTestCase(ModelResponseMetadataMixin, SimpleTestCase):
  """Test the request logs models."""

  def test_initial_values(self) -> None :
    """Test initial values."""
    # Execute result.
    response = ResponseMetadata()
    # Assert result.
    self.assertTrue(response.is_in_progress)
    self.assertEqual('IN_PROGRESS', response.meta_response_status)
    self.assertEqual(timedelta(0), response.logged_duration)
    self.assertEqual(timedelta(0), response.reported_duration)

  @patch('microservice.models.logs.abstract_response.parse_timestamp')
  def test_log_response(self, timestamp: MagicMock) -> None :
    """Test logging a response."""
    for status in StatusCode:
      with self.subTest(status = status.name):
        # Prepare data.
        request = self.get_model_for_response_saving(model_type = ResponseMetadata)
        timestamp.return_value = request.meta_response_logged_timestamp
        response = GrpcResponse()
        response.status = status.name
        response.timestamp.FromDatetime(request.meta_response_logged_timestamp)
        # Execute test.
        request.log_response(grpc_response = response)
        # Assert result.
        self.assertEqual(response.status, request.meta_response_status)
        self.assertEqual(
          response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
          request.meta_response_reported_timestamp,
        )
        self.assertFalse(request.is_in_progress)
        self.assertLess(timedelta(0), request.logged_duration)
        self.assertLess(timedelta(0), request.reported_duration)

  @patch('microservice.models.logs.abstract_response.parse_timestamp')
  def test_log_empty_response(self, timestamp: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    request = self.get_model_for_response_saving(model_type = ResponseMetadata)
    timestamp.return_value = datetime.min.replace(tzinfo = timezone.utc)
    response = GrpcResponse()
    # Execute test.
    request.log_response(grpc_response = response)
    # Assert result.
    self.assertIn('Response status', request.meta_response_logging_errors)
    self.assertFalse(request.is_in_progress)
    self.assertLess(timedelta(0), request.logged_duration)
    self.assertEqual(timedelta(0), request.reported_duration)

  def test_to_grpc(self) -> None :
    """Test that general mapping to gRPC works."""
    for user_label, user_type in User.UserType.items():
      for status in StatusCode:
        with self.subTest(user = user_label, status = status.name):
          # Prepare data.
          request = ResponseMetadata(
            **self.model_full_request_metadata(user = user_type, status = status),
          )
          result = GrpcRequestResponse()
          # Execute test.
          request.response_to_grpc(
            metadata = result.response_metadata,
            response = result.response,
            processed = result.processed_response,
          )
          # Assert result.
          self.assert_grpc_response_metadata(
            model                   = request,
            grpc_response           = result.response,
            grpc_response_response  = result.response_metadata,
            grpc_response_processed = result.processed_response,
          )


  def test_empty_to_grpc(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = ResponseMetadata(**self.model_empty_request_metadata())
    result = GrpcRequestResponse()
    # Execute test.
    request.response_to_grpc(
      metadata = result.response_metadata,
      response = result.response,
      processed = result.processed_response,
    )
    # Assert result.
    self.assertIsNotNone(result)
    self.assertEqual(0            , result.processed_response.logged_duration.nanos)
    self.assertEqual(0            , result.processed_response.reported_duration.nanos)
