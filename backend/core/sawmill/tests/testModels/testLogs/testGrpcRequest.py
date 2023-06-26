"""Test the request logs."""

# pylint:disable=duplicate-code

# Python.
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.testUtil.grpc import GrpcTestMixin
from khaleesi.core.testUtil.testCase import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import (
  GrpcRequest as GrpcGrpcRequest,
  GrpcResponseRequest as GrpcGrpcResponse,
)
from microservice.models import GrpcRequest
from microservice.testUtil import ModelResponseMetadataMixin


class GrpcRequestManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the request logs objects manager."""

  @patch('microservice.models.logs.grpcRequest.parseString')
  @patch.object(GrpcRequest.objects.model, 'logMetadata')
  def testLogRequest(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging a gRPC request."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        metadata.reset_mock()
        metadata.return_value = {}
        string.return_value   = 'parsed-string'
        grpcRequest = GrpcGrpcRequest()
        self.setRequestMetadata(requestMetadata = grpcRequest.requestMetadata, user = userType)
        grpcRequest.upstreamRequest.grpcRequestId   = string.return_value
        grpcRequest.upstreamRequest.khaleesiGate    = string.return_value
        grpcRequest.upstreamRequest.khaleesiService = string.return_value
        grpcRequest.upstreamRequest.grpcService     = string.return_value
        grpcRequest.upstreamRequest.grpcMethod      = string.return_value
        # Execute test.
        result = GrpcRequest.objects.logRequest(grpcRequest = grpcRequest)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpcRequest.requestMetadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                         , metadata.call_args.kwargs['errors'])
        self.assertEqual(
          grpcRequest.upstreamRequest.grpcRequestId,
          result.upstreamRequestGrpcRequestId,
        )
        self.assertEqual(
          grpcRequest.upstreamRequest.khaleesiGate,
          result.upstreamRequestKhaleesiGate,
        )
        self.assertEqual(
          grpcRequest.upstreamRequest.khaleesiService,
          result.upstreamRequestKhaleesiService,
        )
        self.assertEqual(
          grpcRequest.upstreamRequest.grpcService,
          result.upstreamRequestGrpcService,
        )
        self.assertEqual(
          grpcRequest.upstreamRequest.grpcMethod,
          result.upstreamRequestGrpcMethod,
        )

  @patch('microservice.models.logs.grpcRequest.parseString')
  @patch.object(GrpcRequest.objects.model, 'logMetadata')
  def testLogRequestEmpty(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging an empty gRPC request."""
    # Prepare data.
    string.return_value   = 'parsed-string'
    metadata.return_value = {}
    grpcRequest           = GrpcGrpcRequest()
    # Execute test.
    result = GrpcRequest.objects.logRequest(grpcRequest = grpcRequest)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.metaLoggingErrors)

  @patch.object(GrpcRequest.objects, 'get')
  def testLogResponse(self, requestMock: MagicMock) -> None :
    """Test logging a gRPC request response."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        request = ModelResponseMetadataMixin.getModelForResponseSaving(modelType = GrpcRequest)
        request.logResponse = MagicMock()  # type: ignore[assignment]
        requestMock.reset_mock()
        requestMock.return_value = request
        grpcResponse = GrpcGrpcResponse()
        grpcResponse.requestMetadata.caller.grpcRequestId = 'request-id'
        grpcResponse.response.status                      = status.name
        grpcResponse.response.timestamp.FromDatetime(request.metaResponseLoggedTimestamp)
        # Execute test.
        result = GrpcRequest.objects.logResponse(grpcResponse = grpcResponse)
        # Assert result.
        result.save.assert_called_once_with()  # type: ignore[attr-defined]
        result.logResponse.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(GrpcRequest.objects, 'get')
  def testLogEmptyResponse(self, requestMock: MagicMock) -> None :
    """Test logging an empty gRPC request response."""
    # Prepare data.
    request = ModelResponseMetadataMixin.getModelForResponseSaving(modelType = GrpcRequest)
    request.logResponse = MagicMock()  # type: ignore[assignment]
    requestMock.return_value = request
    grpcResponse = GrpcGrpcResponse()
    # Execute test.
    result = GrpcRequest.objects.logResponse(grpcResponse = grpcResponse)
    # Assert result.
    result.save.assert_called_once_with()  # type: ignore[attr-defined]
    result.logResponse.assert_called_once()  # type: ignore[attr-defined]


class GrpcRequestTestCase(ModelResponseMetadataMixin, SimpleTestCase):
  """Test the request logs models."""

  def testToGrpcRequest(self) -> None :
    """Test that general mapping to gRPC works."""
    for userLabel, userType in User.UserType.items():
      for status in StatusCode:
        with self.subTest(user = userLabel, status = status.name):
          # Prepare data.
          request = GrpcRequest(
            upstreamRequestGrpcRequestId   = '',
            upstreamRequestKhaleesiGate    = '',
            upstreamRequestKhaleesiService = '',
            upstreamRequestGrpcService     = '',
            upstreamRequestGrpcMethod      = '',
            **self.modelFullRequestMetadata(user = userType, status = status),
          )
          # Execute test.
          result = request.toGrpc()
          # Assert result.
          self.assertGrpcRequestMetadata(
            model        = request,
            grpc         = result.request.requestMetadata,
            grpcResponse = result.requestMetadata,
          )
          self.assertGrpcResponseMetadata(
            model                 = request,
            grpcResponse          = result.response,
            grpcResponseResponse  = result.responseMetadata,
            grpcResponseProcessed = result.processedResponse,
          )
          self.assertEqual(
            request.upstreamRequestGrpcRequestId,
            result.request.upstreamRequest.grpcRequestId,
          )
          self.assertEqual(
            request.upstreamRequestKhaleesiGate,
            result.request.upstreamRequest.khaleesiGate,
          )
          self.assertEqual(
            request.upstreamRequestKhaleesiService,
            result.request.upstreamRequest.khaleesiService,
          )
          self.assertEqual(
            request.upstreamRequestGrpcService,
            result.request.upstreamRequest.grpcService,
          )
          self.assertEqual(
            request.upstreamRequestGrpcMethod,
            result.request.upstreamRequest.grpcMethod,
          )


  def testEmptyToGrpcRequest(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = GrpcRequest(**self.modelEmptyRequestMetadata())
    # Execute test.
    result = request.toGrpc()
    # Assert result.
    self.assertIsNotNone(result)
