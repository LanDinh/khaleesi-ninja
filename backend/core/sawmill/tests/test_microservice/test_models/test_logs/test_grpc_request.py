"""Test the request logs."""

# Python.
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest as GrpcGrpcRequest,
  GrpcResponseRequest as GrpcGrpcResponse,
)
from microservice.models import GrpcRequest
from microservice.test_util import ModelResponseMetadataMixin


class GrpcRequestManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the request logs objects manager."""

  @patch('microservice.models.logs.grpc_request.parse_string')
  @patch.object(GrpcRequest.objects.model, 'log_metadata')
  def test_log_request(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging a gRPC request."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        metadata.reset_mock()
        metadata.return_value = {}
        string.return_value = 'parsed-string'
        grpc_request = GrpcGrpcRequest()
        self.set_request_metadata(
          request_metadata = grpc_request.requestMetadata,
          user = user_type,
        )
        grpc_request.upstreamRequest.grpcRequestId   = string.return_value
        grpc_request.upstreamRequest.khaleesiGate    = string.return_value
        grpc_request.upstreamRequest.khaleesiService = string.return_value
        grpc_request.upstreamRequest.grpcService     = string.return_value
        grpc_request.upstreamRequest.grpcMethod      = string.return_value
        # Execute test.
        result = GrpcRequest.objects.log_request(grpc_request = grpc_request)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpc_request.requestMetadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                          , metadata.call_args.kwargs['errors'])
        self.assertEqual(
          grpc_request.upstreamRequest.grpcRequestId,
          result.upstream_request_grpc_request_id,
        )
        self.assertEqual(
          grpc_request.upstreamRequest.khaleesiGate,
          result.upstream_request_khaleesi_gate,
        )
        self.assertEqual(
          grpc_request.upstreamRequest.khaleesiService,
          result.upstream_request_khaleesi_service,
        )
        self.assertEqual(
          grpc_request.upstreamRequest.grpcService,
          result.upstream_request_grpc_service,
        )
        self.assertEqual(
          grpc_request.upstreamRequest.grpcMethod,
          result.upstream_request_grpc_method,
        )

  @patch('microservice.models.logs.grpc_request.parse_string')
  @patch.object(GrpcRequest.objects.model, 'log_metadata')
  def test_log_request_empty(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging an empty gRPC request."""
    # Prepare data.
    string.return_value = 'parsed-string'
    metadata.return_value = {}
    grpc_request = GrpcGrpcRequest()
    # Execute test.
    result = GrpcRequest.objects.log_request(grpc_request = grpc_request)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)

  @patch.object(GrpcRequest.objects, 'get')
  def test_log_response(self, request_mock: MagicMock) -> None :
    """Test logging a gRPC request response."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        request = ModelResponseMetadataMixin.get_model_for_response_saving(model_type = GrpcRequest)
        request.log_response = MagicMock()  # type: ignore[assignment]
        request_mock.reset_mock()
        request_mock.return_value = request
        grpc_response = GrpcGrpcResponse()
        grpc_response.requestMetadata.caller.grpcRequestId = 'request-id'
        grpc_response.response.status                      = status.name
        grpc_response.response.timestamp.FromDatetime(request.meta_response_logged_timestamp)
        # Execute test.
        result = GrpcRequest.objects.log_response(grpc_response = grpc_response)
        # Assert result.
        result.save.assert_called_once_with()  # type: ignore[attr-defined]
        result.log_response.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(GrpcRequest.objects, 'get')
  def test_log_empty_response(self, request_mock: MagicMock) -> None :
    """Test logging an empty gRPC request response."""
    # Prepare data.
    request = ModelResponseMetadataMixin.get_model_for_response_saving(model_type = GrpcRequest)
    request.log_response = MagicMock()  # type: ignore[assignment]
    request_mock.return_value = request
    grpc_response = GrpcGrpcResponse()
    # Execute test.
    result = GrpcRequest.objects.log_response(grpc_response = grpc_response)
    # Assert result.
    result.save.assert_called_once_with()  # type: ignore[attr-defined]
    result.log_response.assert_called_once()  # type: ignore[attr-defined]


class GrpcRequestTestCase(ModelResponseMetadataMixin, SimpleTestCase):
  """Test the request logs models."""

  def test_to_grpc_request(self) -> None :
    """Test that general mapping to gRPC works."""
    for user_label, user_type in User.UserType.items():
      for status in StatusCode:
        with self.subTest(user = user_label, status = status.name):
          # Prepare data.
          request = GrpcRequest(
            upstream_request_grpc_request_id  = '',
            upstream_request_khaleesi_gate    = '',
            upstream_request_khaleesi_service = '',
            upstream_request_grpc_service     = '',
            upstream_request_grpc_method      = '',
            **self.model_full_request_metadata(user = user_type, status = status),
          )
          # Execute test.
          result = request.to_grpc_request_response()
          # Assert result.
          self.assert_grpc_request_metadata(
            model         = request,
            grpc          = result.request.requestMetadata,
            grpc_response = result.requestMetadata,
          )
          self.assert_grpc_response_metadata(
            model                   = request,
            grpc_response           = result.response,
            grpc_response_response  = result.responseMetadata,
            grpc_response_processed = result.processedResponse,
          )
          self.assertEqual(
            request.upstream_request_grpc_request_id,
            result.request.upstreamRequest.grpcRequestId,
          )
          self.assertEqual(
            request.upstream_request_khaleesi_gate,
            result.request.upstreamRequest.khaleesiGate,
          )
          self.assertEqual(
            request.upstream_request_khaleesi_service,
            result.request.upstreamRequest.khaleesiService,
          )
          self.assertEqual(
            request.upstream_request_grpc_service,
            result.request.upstreamRequest.grpcService,
          )
          self.assertEqual(
            request.upstream_request_grpc_method,
            result.request.upstreamRequest.grpcMethod,
          )


  def test_empty_to_grpc_request(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = GrpcRequest(**self.model_empty_request_metadata())
    # Execute test.
    result = request.to_grpc_request_response()
    # Assert result.
    self.assertIsNotNone(result)
