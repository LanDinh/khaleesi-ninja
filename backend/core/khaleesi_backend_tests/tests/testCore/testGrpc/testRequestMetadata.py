"""Test grpc utility."""

# Python.
from datetime import datetime, timezone
from unittest.mock import MagicMock
from typing import Any

# khaleesi.ninja.
from khaleesi.core.grpc.requestMetadata import (
  addRequestMetadata,
  addGrpcServerSystemRequestMetadata,
)
from khaleesi.core.shared.state import STATE, UserType
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata


class GrpcTestCase(SimpleTestCase):
  """Test grpc utility."""

  def testAddGrpcServerSystemRequestMetadata(self) -> None :
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
    addGrpcServerSystemRequestMetadata(
      request       = request,
      grpcMethod    = 'LIFECYCLE',
      httpRequestId = 'http-request',
      grpcRequestId = 'grpc-request',
    )
    # Assert result
    self._assertMetadata(request = request, expected = expected, userType = UserType.SYSTEM)

  def testAddRequestMetadata(self) -> None :
    """Test adding request metadata."""
    # Prepare data.
    expected = RequestMetadata()
    expected.caller.httpRequestId = 'http-request'
    expected.caller.grpcRequestId = 'grpc-request-id'
    expected.caller.grpcService   = 'grpc-service'
    expected.caller.grpcMethod    = 'grpc-method'
    expected.user.id              = 'user-id'
    for userType in UserType:
      with self.subTest(user = userType.name):
        request = MagicMock()
        request.requestMetadata = RequestMetadata()
        STATE.reset()
        STATE.request.httpRequestId = expected.caller.httpRequestId
        STATE.request.grpcRequestId = expected.caller.grpcRequestId
        STATE.request.grpcService   = expected.caller.grpcService
        STATE.request.grpcMethod    = expected.caller.grpcMethod
        STATE.user.type   = userType
        STATE.user.userId = expected.user.id
        # Execute test.
        addRequestMetadata(request = request)
        # Assert result.
        self._assertMetadata(request = request, expected = expected, userType = userType)
        STATE.reset()

  def _assertMetadata(
      self, *,
      request: Any,
      expected: RequestMetadata,
      userType: UserType,
  ) -> None :
    """Asset that the metadata is as expected."""
    # Manual values.
    self.assertEqual(expected.caller.httpRequestId, request.requestMetadata.caller.httpRequestId)
    self.assertEqual(expected.caller.grpcRequestId, request.requestMetadata.caller.grpcRequestId)
    self.assertEqual(expected.caller.grpcService  , request.requestMetadata.caller.grpcService)
    self.assertEqual(expected.caller.grpcMethod   , request.requestMetadata.caller.grpcMethod)
    self.assertEqual(expected.user.id             , request.requestMetadata.user.id)
    self.assertEqual(userType                     , UserType(request.requestMetadata.user.type))
    # Automatic values.
    self.assertEqual('core'                  , request.requestMetadata.caller.khaleesiGate)
    self.assertEqual('khaleesi_backend_tests', request.requestMetadata.caller.khaleesiService)
    self.assertIsNotNone(request.requestMetadata.caller.podId)
    now = datetime.now(tz = timezone.utc)
    self.assertEqual(now.date(), request.requestMetadata.timestamp.ToDatetime().date())
