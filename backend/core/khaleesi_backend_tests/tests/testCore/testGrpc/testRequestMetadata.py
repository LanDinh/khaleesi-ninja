"""Test grpc utility."""

# Python.
from datetime import datetime, timezone

# khaleesi.ninja.
from khaleesi.core.grpc.requestMetadata import addRequestMetadata, addSystemRequestMetadata
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User


class GrpcTestCase(SimpleTestCase):
  """Test grpc utility."""

  def testAddSystemRequestMetadata(self) -> None :
    """Test adding request metadata for grpc server system actions."""
    # Prepare data.
    metadata = RequestMetadata()
    httpRequestId = 'http-request'
    grpcRequestId = 'grpc-request'
    # Execute test.
    addSystemRequestMetadata(
      metadata      = metadata,
      grpcMethod    = 'LIFECYCLE',
      httpRequestId = httpRequestId,
      grpcRequestId = grpcRequestId,
    )
    # Assert result.
    self.assertEqual(httpRequestId, metadata.httpCaller.requestId)
    self.assertEqual('core'       , metadata.httpCaller.khaleesiGate)
    self.assertEqual('/'          , metadata.httpCaller.path)
    self.assertEqual(''           , metadata.httpCaller.podId)
    self.assertEqual(grpcRequestId, metadata.grpcCaller.requestId)
    self.assertEqual('grpc-server', metadata.grpcCaller.grpcService)
    self.assertEqual('lifecycle'  , metadata.grpcCaller.grpcMethod)
    self.assertEqual('grpc-server'       , metadata.user.id)
    self.assertEqual(User.UserType.SYSTEM, metadata.user.type)
    self._assertMetadata(metadata = metadata)

  def testAddRequestMetadata(self) -> None :
    """Test adding request metadata."""
    # Prepare data.
    metadata = RequestMetadata()
    # Execute test.
    addRequestMetadata(metadata = metadata)
    # Assert result.
    self._assertMetadata(metadata = metadata)

  def _assertMetadata(self, *, metadata: RequestMetadata) -> None :
    """Asset that the metadata is as expected."""
    # Automatic values.
    self.assertEqual('core'                  , metadata.grpcCaller.khaleesiGate)
    self.assertEqual('khaleesi_backend_tests', metadata.grpcCaller.khaleesiService)
    self.assertIsNotNone(metadata.grpcCaller.podId)
    now = datetime.now(tz = timezone.utc)
    self.assertEqual(now.date(), metadata.timestamp.ToDatetime().date())
