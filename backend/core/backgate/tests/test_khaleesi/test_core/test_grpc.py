"""Test grpc utility."""

# Python.
from datetime import datetime, timezone
from unittest.mock import MagicMock
from typing import Any

# khaleesi.ninja.
from khaleesi.core.grpc import add_request_metadata, add_logging_metadata
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import LoggingMetadata


class GrpcTestCase(SimpleTestCase):
  """Test grpc utility."""

  metadata = {
      'request_id'  : 'request-id',
      'grpc_service': 'grpc-server',
      'grpc_method' : 'grpc-method',
      'user_id'     : 'user-id',
  }

  def test_add_request_metadata(self) -> None :
    """Test adding request metadata."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        request = MagicMock()
        request.request_metadata = RequestMetadata()
        # Execute test.
        add_request_metadata(request = request, user_type = user_type, **self.metadata)
        # Assert result.
        self.assert_metadata(request = request, user_type =  user_type)

  def test_add_logging_metadata(self) -> None :
    """Test adding logging metadata."""
    for user_label, user_type in User.UserType.items():
      with self.subTest(user = user_label):
        # Prepare data.
        request = MagicMock()
        request.request_metadata = RequestMetadata()
        request.logging_metadata = LoggingMetadata()
        # Execute test.
        add_logging_metadata(request = request, user_type = user_type, **self.metadata)
        # Assert result.
        self.assert_metadata(request = request, user_type =  user_type)

  def assert_metadata(self, *, request: Any, user_type: 'User.UserType.V') -> None :
    """Asset that the metadata is as expected."""
    # Manual values.
    self.assertEqual(request.request_metadata.caller.request_id  , self.metadata['request_id'])
    self.assertEqual(request.request_metadata.caller.grpc_service, self.metadata['grpc_service'])
    self.assertEqual(request.request_metadata.caller.grpc_method , self.metadata['grpc_method'])
    self.assertEqual(request.request_metadata.user.id            , self.metadata['user_id'])
    self.assertEqual(request.request_metadata.user.type          , user_type)
    # Automatic values.
    self.assertEqual(request.request_metadata.caller.khaleesi_gate   , 'core')
    self.assertEqual(request.request_metadata.caller.khaleesi_service, 'backgate')

  def assert_logging_metadata(self, *, request: Any) -> None :
    """Asset that the metadata is as expected."""
    # Manual values.
    self.assertEqual(request.logging_metadata.logger.grpc_service, self.metadata['grpc_service'])
    self.assertEqual(request.logging_metadata.logger.grpc_method , self.metadata['grpc_method'])
    # Automatic values.
    self.assertEqual(request.logging_metadata.caller.khaleesi_gate   , 'core')
    self.assertEqual(request.logging_metadata.caller.khaleesi_service, 'backgate')
    now = datetime.now(tz = timezone.utc)
    self.assertEqual(now.date(), request.logging_metadata.timestamp.ToDatetime.date())
