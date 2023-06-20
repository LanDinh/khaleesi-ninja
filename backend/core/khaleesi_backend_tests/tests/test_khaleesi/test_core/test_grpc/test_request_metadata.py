"""Test grpc utility."""

# Python.
from datetime import datetime, timezone
from unittest.mock import MagicMock
from typing import Any

# khaleesi.ninja.
from khaleesi.core.grpc.request_metadata import (
  add_request_metadata,
  add_grpc_server_system_request_metadata,
)
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata


class GrpcTestCase(SimpleTestCase):
  """Test grpc utility."""

  def test_add_grpc_server_system_request_metadata(self) -> None :
    """Test adding request metadata for grpc server system actions."""
    # Prepare data.
    request = MagicMock()
    request.requestMetadata = RequestMetadata()
    expected = RequestMetadata()
    expected.caller.httpRequestId = 'http-request'
    expected.caller.grpcRequestId = 'grpc-request'
    expected.caller.grpcService   = 'grpc-server'
    expected.caller.grpcMethod    = 'lifecycle'
    expected.user.id              = 'grpc-server'
    # Execute test.
    add_grpc_server_system_request_metadata(
      request         = request,
      grpc_method     = 'LIFECYCLE',
      http_request_id = 'http-request',
      grpc_request_id = 'grpc-request',
    )
    # Assert result
    self._assert_metadata(request = request, expected = expected, user_type = UserType.SYSTEM)

  def test_add_request_metadata(self) -> None :
    """Test adding request metadata."""
    # Prepare data.
    expected = RequestMetadata()
    expected.caller.httpRequestId = 'http-request'
    expected.caller.grpcRequestId = 'grpc-request-id'
    expected.caller.grpcService   = 'grpc-service'
    expected.caller.grpcMethod    = 'grpc-method'
    expected.user.id              = 'user-id'
    for user_type in UserType:
      with self.subTest(user = user_type.name):
        request = MagicMock()
        request.requestMetadata = RequestMetadata()
        STATE.reset()
        STATE.request.http_request_id = expected.caller.httpRequestId
        STATE.request.grpc_request_id = expected.caller.grpcRequestId
        STATE.request.grpc_service    = expected.caller.grpcService
        STATE.request.grpc_method     = expected.caller.grpcMethod
        STATE.user.type    = user_type
        STATE.user.user_id = expected.user.id
        # Execute test.
        add_request_metadata(request = request)
        # Assert result.
        self._assert_metadata(request = request, expected = expected, user_type = user_type)
        STATE.reset()

  def _assert_metadata(
      self, *,
      request: Any,
      expected: RequestMetadata,
      user_type: UserType,
  ) -> None :
    """Asset that the metadata is as expected."""
    # Manual values.
    self.assertEqual(expected.caller.httpRequestId, request.requestMetadata.caller.httpRequestId)
    self.assertEqual(expected.caller.grpcRequestId, request.requestMetadata.caller.grpcRequestId)
    self.assertEqual(expected.caller.grpcService  , request.requestMetadata.caller.grpcService)
    self.assertEqual(expected.caller.grpcMethod   , request.requestMetadata.caller.grpcMethod)
    self.assertEqual(expected.user.id             , request.requestMetadata.user.id)
    self.assertEqual(user_type                    , UserType(request.requestMetadata.user.type))
    # Automatic values.
    self.assertEqual('core'                  , request.requestMetadata.caller.khaleesiGate)
    self.assertEqual('khaleesi_backend_tests', request.requestMetadata.caller.khaleesiService)
    self.assertIsNotNone(request.requestMetadata.caller.podId)
    now = datetime.now(tz = timezone.utc)
    self.assertEqual(now.date(), request.requestMetadata.timestamp.ToDatetime().date())
