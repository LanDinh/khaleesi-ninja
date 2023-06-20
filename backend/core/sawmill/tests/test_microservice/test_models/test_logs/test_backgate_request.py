"""Test the HTTP request logs."""

# Python.
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import (
  HttpRequest as GrpcHttpRequest,
  EmptyRequest as GrpcEmptyRequest,
  HttpRequestResponse as GrpcHttpResponse,
  HttpResponseRequest as GrpcHttpResponseRequest,
)
from microservice.models import HttpRequest
from microservice.test_util import ModelResponseMetadataMixin


class HttpRequestManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the HTTP request logs objects manager."""

  @patch('microservice.models.logs.http_request.parse_string', return_value = 'parsed-string')
  @patch.object(HttpRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_request(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging of a gRPC HTTP request."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        metadata.reset_mock()
        grpc_request = GrpcHttpRequest()
        self.set_request_metadata(
          request_metadata = grpc_request.requestMetadata,
          user = user_type,
        )
        grpc_request.language       = string.return_value
        grpc_request.deviceId       = string.return_value
        grpc_request.languageHeader = string.return_value
        grpc_request.ip             = string.return_value
        grpc_request.useragent      = string.return_value
        # Execute test.
        result = HttpRequest.objects.log_request(grpc_request = grpc_request)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpc_request.requestMetadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                          , metadata.call_args.kwargs['errors'])
        self.assertEqual(grpc_request.language       , result.language)
        self.assertEqual(grpc_request.deviceId       , result.device_id)
        self.assertEqual(grpc_request.languageHeader , result.language_header)
        self.assertEqual(grpc_request.ip             , result.ip)
        self.assertEqual(grpc_request.useragent      , result.useragent)
        self.assertEqual(
          GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.USER),
          result.type,
        )

  @patch('microservice.models.logs.http_request.parse_string', return_value = 'parsed-string')
  @patch.object(HttpRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_request_empty(self, metadata: MagicMock, _: MagicMock) -> None :
    """Test logging an empty gRPC HTTP request."""
    # Prepare data.
    grpc_request = GrpcHttpRequest()
    # Execute test.
    result = HttpRequest.objects.log_request(grpc_request = grpc_request)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)
    self.assertEqual(
      GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.USER),
      result.type,
    )

  @patch.object(HttpRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_system_request(self, metadata: MagicMock) -> None :
    """Test logging of a gRPC system HTTP request."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        metadata.reset_mock()
        grpc_request = GrpcEmptyRequest()
        self.set_request_metadata(
          request_metadata = grpc_request.requestMetadata,
          user = user_type,
        )
        # Execute test.
        result = HttpRequest.objects.log_system_request(grpc_request = grpc_request)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpc_request.requestMetadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                          , metadata.call_args.kwargs['errors'])
        self.assertEqual('UNKNOWN'                   , result.language)
        self.assertEqual('UNKNOWN'                   , result.device_id)
        self.assertEqual('UNKNOWN'                   , result.language_header)
        self.assertEqual('UNKNOWN'                   , result.ip)
        self.assertEqual('UNKNOWN'                   , result.useragent)
        self.assertEqual(
          GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.SYSTEM),
          result.type,
        )

  @patch.object(HttpRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_system_request_empty(self, metadata: MagicMock) -> None :
    """Test logging an empty gRPC system HTTP request."""
    # Prepare data.
    grpc_request = GrpcEmptyRequest()
    # Execute test.
    result = HttpRequest.objects.log_system_request(grpc_request = grpc_request)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)
    self.assertEqual(
      GrpcHttpResponse.RequestType.Name(GrpcHttpResponse.RequestType.SYSTEM),
      result.type,
    )

  @patch.object(HttpRequest.objects, 'get')
  def test_log_response(self, request_mock: MagicMock) -> None :
    """Test logging a gRPC HTTP request response."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        request = ModelResponseMetadataMixin.get_model_for_response_saving(
          model_type = HttpRequest,
        )
        request.log_response = MagicMock()  # type: ignore[assignment]
        request_mock.reset_mock()
        request_mock.return_value = request
        grpc_response = GrpcHttpResponseRequest()
        grpc_response.requestMetadata.caller.httpRequestId = 'request-id'
        grpc_response.response.status                      = status.name
        grpc_response.response.timestamp.FromDatetime(request.meta_response_logged_timestamp)
        # Execute test.
        result = HttpRequest.objects.log_response(grpc_response = grpc_response)
        # Assert result.
        result.save.assert_called_once_with()  # type: ignore[attr-defined]
        result.log_response.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(HttpRequest.objects, 'get')
  def test_log_empty_response(self, request_mock: MagicMock) -> None :
    """Test logging an empty gRPC HTTP request response."""
    # Prepare data.
    request = ModelResponseMetadataMixin.get_model_for_response_saving(model_type = HttpRequest)
    request.log_response = MagicMock()  # type: ignore[assignment]
    request_mock.reset_mock()
    request_mock.return_value = request
    grpc_response = GrpcHttpResponseRequest()
    # Execute test.
    result = HttpRequest.objects.log_response(grpc_response = grpc_response)
    # Assert result.
    result.save.assert_called_once_with()  # type: ignore[attr-defined]
    result.log_response.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(HttpRequest.objects, 'get')
  def test_add_child_duration(self, request_mock: MagicMock) -> None :
    """Test adding child durations."""
    # Prepare data.
    request = ModelResponseMetadataMixin.get_model_for_response_saving(model_type = HttpRequest)
    request.save = MagicMock()  # type: ignore[assignment]
    request_mock.reset_mock()
    request_mock.return_value = request
    # Execute test.
    HttpRequest.objects.add_child_duration(request = MagicMock())
    # Assert result.
    request.save.assert_called_once_with()


class HttpRequestTestCase(ModelResponseMetadataMixin, SimpleTestCase):
  """Test the HTTP request logs models."""

  def test_to_grpc_request(self) -> None :
    """Test that general mapping to gRPC works."""
    for user_label, user_type in User.UserType.items():
      for type_label, type_type in GrpcHttpResponse.RequestType.items():
        for status in StatusCode:
          with self.subTest(user = user_label, type = type_label, status = status):
            # Prepare data.
            request = HttpRequest(
              language        = 'language',
              device_id       = 'device-id',
              language_header = 'language-header',
              ip              = 'ip',
              useragent       = 'useragent',
              type            = type_label,
              **self.model_full_request_metadata(user = user_type, status = status),
            )
            # Execute test.
            result = request.to_grpc_backgate_request_response()
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
            self.assertEqual(request.language       , result.request.language)
            self.assertEqual(request.device_id      , result.request.deviceId)
            self.assertEqual(request.language_header, result.request.languageHeader)
            self.assertEqual(request.ip             , result.request.ip)
            self.assertEqual(request.useragent      , result.request.useragent)
            self.assertEqual(type_type              , result.type)


  def test_empty_to_grpc_request(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = HttpRequest(**self.model_empty_request_metadata())
    # Execute test.
    result = request.to_grpc_backgate_request_response()
    # Assert result.
    self.assertIsNotNone(result)
    self.assertEqual(GrpcHttpResponse.RequestType.UNKNOWN, result.type)
