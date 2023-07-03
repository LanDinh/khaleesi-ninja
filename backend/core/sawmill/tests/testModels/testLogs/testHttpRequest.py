"""Test the HTTP request logs."""

# pylint:disable=duplicate-code

# Python.
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.testUtil.grpc import GrpcTestMixin
from khaleesi.core.testUtil.testCase import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User, EmptyRequest as GrpcEmptyRequest
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequest as GrpcHttpRequest,
  HttpRequestResponse as GrpcHttpResponse,
  HttpResponseRequest as GrpcHttpResponseRequest,
)
from microservice.models import HttpRequest
from microservice.testUtil import ModelResponseMetadataMixin


class HttpRequestManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the HTTP request logs objects manager."""

  @patch('microservice.models.logs.httpRequest.parseString', return_value = 'parsed-string')
  @patch.object(HttpRequest.objects.model, 'logMetadata', return_value = {})
  def testLogRequest(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging of a gRPC HTTP request."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        metadata.reset_mock()
        grpcRequest = GrpcHttpRequest()
        self.setRequestMetadata(requestMetadata = grpcRequest.requestMetadata, user = userType)
        grpcRequest.language       = string.return_value
        grpcRequest.deviceId       = string.return_value
        grpcRequest.languageHeader = string.return_value
        grpcRequest.ip             = string.return_value
        grpcRequest.useragent      = string.return_value
        # Execute test.
        result = HttpRequest.objects.logRequest(grpcRequest = grpcRequest)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpcRequest.requestMetadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                         , metadata.call_args.kwargs['errors'])
        self.assertEqual(grpcRequest.language       , result.language)
        self.assertEqual(grpcRequest.deviceId       , result.deviceId)
        self.assertEqual(grpcRequest.languageHeader , result.languageHeader)
        self.assertEqual(grpcRequest.ip             , result.ip)
        self.assertEqual(grpcRequest.useragent      , result.useragent)
        self.assertEqual(
          GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.USER),
          result.type,
        )

  @patch('microservice.models.logs.httpRequest.parseString', return_value = 'parsed-string')
  @patch.object(HttpRequest.objects.model, 'logMetadata', return_value = {})
  def testLogRequestEmpty(self, metadata: MagicMock, _: MagicMock) -> None :
    """Test logging an empty gRPC HTTP request."""
    # Prepare data.
    grpcRequest = GrpcHttpRequest()
    # Execute test.
    result = HttpRequest.objects.logRequest(grpcRequest = grpcRequest)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.metaLoggingErrors)
    self.assertEqual(
      GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.USER),
      result.type,
    )

  @patch.object(HttpRequest.objects.model, 'logMetadata', return_value = {})
  def testLogSystemRequest(self, metadata: MagicMock) -> None :
    """Test logging of a gRPC system HTTP request."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        metadata.reset_mock()
        grpcRequest = GrpcEmptyRequest()
        self.setRequestMetadata(requestMetadata = grpcRequest.requestMetadata, user = userType)
        # Execute test.
        result = HttpRequest.objects.logSystemRequest(grpcRequest = grpcRequest)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpcRequest.requestMetadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                         , metadata.call_args.kwargs['errors'])
        self.assertEqual('UNKNOWN'                  , result.language)
        self.assertEqual('UNKNOWN'                  , result.deviceId)
        self.assertEqual('UNKNOWN'                  , result.languageHeader)
        self.assertEqual('UNKNOWN'                  , result.ip)
        self.assertEqual('UNKNOWN'                  , result.useragent)
        self.assertEqual(
          GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.SYSTEM),
          result.type,
        )

  @patch.object(HttpRequest.objects.model, 'logMetadata', return_value = {})
  def testLogSystemRequestEmpty(self, metadata: MagicMock) -> None :
    """Test logging an empty gRPC system HTTP request."""
    # Prepare data.
    grpcRequest = GrpcEmptyRequest()
    # Execute test.
    result = HttpRequest.objects.logSystemRequest(grpcRequest = grpcRequest)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.metaLoggingErrors)
    self.assertEqual(
      GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.SYSTEM),
      result.type,
    )

  @patch.object(HttpRequest.objects, 'get')
  def testLogResponse(self, requestMock: MagicMock) -> None :
    """Test logging a gRPC HTTP request response."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        request = ModelResponseMetadataMixin.getModelForResponseSaving(modelType = HttpRequest)
        request.logResponse = MagicMock()  # type: ignore[assignment]
        requestMock.reset_mock()
        requestMock.return_value = request
        grpcResponse = GrpcHttpResponseRequest()
        grpcResponse.requestMetadata.httpCaller.requestId = 'request-id'
        grpcResponse.response.status                      = status.name
        grpcResponse.response.timestamp.FromDatetime(request.metaResponseLoggedTimestamp)
        # Execute test.
        result = HttpRequest.objects.logResponse(grpcResponse = grpcResponse)
        # Assert result.
        result.save.assert_called_once_with()  # type: ignore[attr-defined]
        result.logResponse.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(HttpRequest.objects, 'get')
  def testLogEmptyResponse(self, requestMock: MagicMock) -> None :
    """Test logging an empty gRPC HTTP request response."""
    # Prepare data.
    request = ModelResponseMetadataMixin.getModelForResponseSaving(modelType = HttpRequest)
    request.logResponse = MagicMock()  # type: ignore[assignment]
    requestMock.reset_mock()
    requestMock.return_value = request
    grpcResponse = GrpcHttpResponseRequest()
    # Execute test.
    result = HttpRequest.objects.logResponse(grpcResponse = grpcResponse)
    # Assert result.
    result.save.assert_called_once_with()  # type: ignore[attr-defined]
    result.logResponse.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(HttpRequest.objects, 'get')
  def testAddChildDuration(self, requestMock: MagicMock) -> None :
    """Test adding child durations."""
    # Prepare data.
    request = ModelResponseMetadataMixin.getModelForResponseSaving(modelType = HttpRequest)
    request.save = MagicMock()  # type: ignore[assignment]
    requestMock.reset_mock()
    requestMock.return_value = request
    # Execute test.
    HttpRequest.objects.addChildDuration(request = MagicMock())
    # Assert result.
    request.save.assert_called_once_with()


class HttpRequestTestCase(ModelResponseMetadataMixin, SimpleTestCase):
  """Test the HTTP request logs models."""

  def testToGrpc(self) -> None :
    """Test that general mapping to gRPC works."""
    for userLabel, userType in User.UserType.items():
      for typeLabel, typeType in GrpcHttpResponse.RequestType.items():
        for status in StatusCode:
          with self.subTest(user = userLabel, type = typeLabel, status = status):
            # Prepare data.
            request = HttpRequest(
              language       = 'language',
              deviceId       = 'device-id',
              languageHeader = 'language-header',
              ip             = 'ip',
              useragent      = 'useragent',
              type           = typeLabel,
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
            self.assertEqual(request.language      , result.request.language)
            self.assertEqual(request.deviceId      , result.request.deviceId)
            self.assertEqual(request.languageHeader, result.request.languageHeader)
            self.assertEqual(request.ip            , result.request.ip)
            self.assertEqual(request.useragent     , result.request.useragent)
            self.assertEqual(typeType              , result.type)


  def testEmptyToGrpc(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = HttpRequest(**self.modelEmptyRequestMetadata())
    # Execute test.
    result = request.toGrpc()
    # Assert result.
    self.assertIsNotNone(result)
    self.assertEqual(GrpcHttpResponse.RequestType.UNKNOWN, result.type)
