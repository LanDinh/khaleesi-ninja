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
    request.request_metadata = RequestMetadata()
    expected = RequestMetadata()
    expected.caller.request_id   = -1
    expected.caller.grpc_service = 'grpc-server'
    expected.caller.grpc_method  = 'lifecycle'
    expected.user.id             = 'grpc-server'
    # Execute test.
    add_grpc_server_system_request_metadata(request = request, grpc_method = 'LIFECYCLE')
    # Assert result
    self.assert_metadata(request = request, expected = expected, user_type = UserType.SYSTEM)

  def test_add_request_metadata(self) -> None :
    """Test adding request metadata."""
    # Prepare data.
    expected = RequestMetadata()
    expected.caller.request_id   = 13
    expected.caller.grpc_service = 'grpc-service'
    expected.caller.grpc_method  = 'grpc-method'
    expected.user.id             = 'user-id'
    for user_type in UserType:
      with self.subTest(user = user_type.name):
        request = MagicMock()
        request.request_metadata = RequestMetadata()
        STATE.reset()
        STATE.request.id           = expected.caller.request_id
        STATE.request.grpc_service = expected.caller.grpc_service
        STATE.request.grpc_method  = expected.caller.grpc_method
        STATE.user.type = user_type
        STATE.user.id   = expected.user.id
        # Execute test.
        add_request_metadata(request = request)
        # Assert result.
        self.assert_metadata(request = request, expected = expected, user_type = user_type)
        STATE.reset()

  def assert_metadata(
      self, *,
      request: Any,
      expected: RequestMetadata,
      user_type: UserType,
  ) -> None :
    """Asset that the metadata is as expected."""
    # Manual values.
    self.assertEqual(expected.caller.request_id  , request.request_metadata.caller.request_id)
    self.assertEqual(expected.caller.grpc_service, request.request_metadata.caller.grpc_service)
    self.assertEqual(expected.caller.grpc_method , request.request_metadata.caller.grpc_method)
    self.assertEqual(expected.user.id            , request.request_metadata.user.id)
    self.assertEqual(user_type                   , UserType(request.request_metadata.user.type))
    # Automatic values.
    self.assertEqual('core'    , request.request_metadata.caller.khaleesi_gate)
    self.assertEqual('backgate', request.request_metadata.caller.khaleesi_service)
    now = datetime.now(tz = timezone.utc)
    self.assertEqual(now.date(), request.request_metadata.timestamp.ToDatetime().date())
