"""Test the backgate request logs."""

# Python.
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import (
  BackgateRequest as GrpcBackgateRequest,
  EmptyRequest as GrpcEmptyRequest,
  BackgateRequestResponse as GrpcBackgateResponse,
  BackgateResponseRequest as GrpcBackgateResponseRequest,
)
from microservice.models import BackgateRequest
from microservice.test_util import ModelResponseMetadataMixin


class BackgateRequestManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the backgate request logs objects manager."""

  @patch('microservice.models.logs.request.parse_string', return_value = 'parsed-string')
  @patch.object(BackgateRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_backgate_request(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging of a gRPC backgate request."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        metadata.reset_mock()
        grpc_request = GrpcBackgateRequest()
        self.set_request_metadata(
          request_metadata = grpc_request.request_metadata,
          user = user_type,
        )
        grpc_request.language        = string.return_value
        grpc_request.device_id       = string.return_value
        grpc_request.language_header = string.return_value
        grpc_request.ip              = string.return_value
        grpc_request.useragent       = string.return_value
        # Execute test.
        result = BackgateRequest.objects.log_backgate_request(grpc_backgate_request = grpc_request)
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpc_request.request_metadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                           , metadata.call_args.kwargs['errors'])
        self.assertEqual(grpc_request.language        , result.language)
        self.assertEqual(grpc_request.device_id       , result.device_id)
        self.assertEqual(grpc_request.language_header , result.language_header)
        self.assertEqual(grpc_request.ip              , result.ip)
        self.assertEqual(grpc_request.useragent       , result.useragent)
        self.assertEqual(
          GrpcBackgateResponse.RequestType.Name(GrpcBackgateResponse.RequestType.USER),
          result.type,
        )

  @patch('microservice.models.logs.event.parse_string', return_value = 'parsed-string')
  @patch.object(BackgateRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_backgate_request_empty(self, metadata: MagicMock, _: MagicMock) -> None :
    """Test logging an empty gRPC request."""
    # Prepare data.
    grpc_request = GrpcBackgateRequest()
    # Execute test.
    result = BackgateRequest.objects.log_backgate_request(grpc_backgate_request = grpc_request)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)
    self.assertEqual(
      GrpcBackgateResponse.RequestType.Name(GrpcBackgateResponse.RequestType.USER),
      result.type,
    )

  @patch.object(BackgateRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_system_backgate_request(self, metadata: MagicMock) -> None :
    """Test logging of a gRPC system backgate request."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        metadata.reset_mock()
        grpc_request = GrpcEmptyRequest()
        self.set_request_metadata(
          request_metadata = grpc_request.request_metadata,
          user = user_type,
        )
        # Execute test.
        result = BackgateRequest.objects.log_system_backgate_request(
          grpc_backgate_request = grpc_request,
        )
        # Assert result.
        metadata.assert_called_once()
        self.assertEqual(grpc_request.request_metadata, metadata.call_args.kwargs['metadata'])
        self.assertEqual([]                           , metadata.call_args.kwargs['errors'])
        self.assertEqual('UNKNOWN'                    , result.language)
        self.assertEqual('UNKNOWN'                    , result.device_id)
        self.assertEqual('UNKNOWN'                    , result.language_header)
        self.assertEqual('UNKNOWN'                    , result.ip)
        self.assertEqual('UNKNOWN'                    , result.useragent)
        self.assertEqual(
          GrpcBackgateResponse.RequestType.Name(GrpcBackgateResponse.RequestType.SYSTEM),
          result.type,
        )

  @patch.object(BackgateRequest.objects.model, 'log_metadata', return_value = {})
  def test_log_system_backgate_request_empty(self, metadata: MagicMock) -> None :
    """Test logging an empty gRPC request."""
    # Prepare data.
    grpc_request = GrpcEmptyRequest()
    # Execute test.
    result = BackgateRequest.objects.log_system_backgate_request(
      grpc_backgate_request = grpc_request,
    )
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)
    self.assertEqual(
      GrpcBackgateResponse.RequestType.Name(GrpcBackgateResponse.RequestType.SYSTEM),
      result.type,
    )

  @patch.object(BackgateRequest.objects, 'get')
  def test_log_response(self, request_mock: MagicMock) -> None :
    """Test logging a gRPC request response."""
    for status in StatusCode:
      with self.subTest(status = status):
        # Prepare data.
        request = ModelResponseMetadataMixin.get_model_for_response_saving(
          model_type = BackgateRequest,
        )
        request.log_response = MagicMock()  # type: ignore[assignment]
        request_mock.reset_mock()
        request_mock.return_value = request
        grpc_response                     = GrpcBackgateResponseRequest()
        grpc_response.request_metadata.caller.backgate_request_id = 'request-id'
        grpc_response.response.status                             = status.name
        grpc_response.response.timestamp.FromDatetime(request.meta_response_logged_timestamp)
        # Execute test.
        result = BackgateRequest.objects.log_response(grpc_response = grpc_response)
        # Assert result.
        result.save.assert_called_once_with()  # type: ignore[attr-defined]
        result.log_response.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(BackgateRequest.objects, 'get')
  def test_log_empty_response(self, request_mock: MagicMock) -> None :
    """Test logging an empty gRPC request response."""
    # Prepare data.
    request = ModelResponseMetadataMixin.get_model_for_response_saving(model_type = BackgateRequest)
    request.log_response = MagicMock()  # type: ignore[assignment]
    request_mock.reset_mock()
    request_mock.return_value = request
    grpc_response = GrpcBackgateResponseRequest()
    # Execute test.
    result = BackgateRequest.objects.log_response(grpc_response = grpc_response)
    # Assert result.
    result.save.assert_called_once_with()  # type: ignore[attr-defined]
    result.log_response.assert_called_once()  # type: ignore[attr-defined]

  @patch.object(BackgateRequest.objects, 'get')
  def test_add_child_duration(self, request_mock: MagicMock) -> None :
    """Test adding child durations."""
    # Prepare data.
    request = ModelResponseMetadataMixin.get_model_for_response_saving(model_type = BackgateRequest)
    request.save = MagicMock()  # type: ignore[assignment]
    request_mock.reset_mock()
    request_mock.return_value = request
    # Execute test.
    BackgateRequest.objects.add_child_duration(request = MagicMock())
    # Assert result.
    request.save.assert_called_once_with()


class BackgateRequestTestCase(ModelResponseMetadataMixin, SimpleTestCase):
  """Test the backgate request logs models."""

  def test_to_grpc_request(self) -> None :
    """Test that general mapping to gRPC works."""
    for user_label, user_type in User.UserType.items():
      for type_label, type_type in GrpcBackgateResponse.RequestType.items():
        for status in StatusCode:
          with self.subTest(user = user_label, type = type_label, status = status):
            # Prepare data.
            request = BackgateRequest(
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
              grpc          = result.request.request_metadata,
              grpc_response = result.request_metadata,
            )
            self.assert_grpc_response_metadata(
              model                   = request,
              grpc_response           = result.response,
              grpc_response_response  = result.response_metadata,
              grpc_response_processed = result.processed_response,
            )
            self.assertEqual(request.language       , result.request.language)
            self.assertEqual(request.device_id      , result.request.device_id)
            self.assertEqual(request.language_header, result.request.language_header)
            self.assertEqual(request.ip             , result.request.ip)
            self.assertEqual(request.useragent      , result.request.useragent)
            self.assertEqual(type_type              , result.type)


  def test_empty_to_grpc_request(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = BackgateRequest(**self.model_empty_request_metadata())
    # Execute test.
    result = request.to_grpc_backgate_request_response()
    # Assert result.
    self.assertIsNotNone(result)
    self.assertEqual(GrpcBackgateResponse.RequestType.UNKNOWN, result.type)
