"""Test the request logs."""

# pylint:disable=duplicate-code

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import GrpcRequestRequest as GrpcGrpcRequest
from microservice.models import GrpcRequest


class GrpcRequestTestCase(SimpleTestCase):
  """Test the request logs models."""

  @patch('microservice.models.logs.grpcRequest.Model.khaleesiSave')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.metadataFromGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.responseMetadataFromGrpc')
  def testKhaleesiSaveNew(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test saving a new instance."""
    # Prepare data.
    instance = GrpcRequest()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = self._createGrpcGrpcRequest()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    metadata.assert_called_once()
    responseMetadata.assert_called_once()
    upstream = grpc.request.upstreamRequest
    self.assertEqual(upstream.requestId      , instance.upstreamRequestId)
    self.assertEqual(upstream.khaleesiGate   , instance.upstreamRequestKhaleesiGate)
    self.assertEqual(upstream.khaleesiService, instance.upstreamRequestKhaleesiService)
    self.assertEqual(upstream.grpcService    , instance.upstreamRequestGrpcService)
    self.assertEqual(upstream.grpcMethod     , instance.upstreamRequestGrpcMethod)
    self.assertEqual(upstream.podId          , instance.upstreamRequestPodId)

  @patch('microservice.models.logs.grpcRequest.Model.khaleesiSave')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.metadataFromGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.responseMetadataFromGrpc')
  def testKhaleesiSaveOld(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test saving an old instance."""
    # Prepare data.
    instance = GrpcRequest()
    instance._state.adding = False  # pylint: disable=protected-access
    grpc = self._createGrpcGrpcRequest()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    metadata.assert_called_once()
    responseMetadata.assert_called_once()
    upstream = grpc.request.upstreamRequest
    self.assertNotEqual(upstream.requestId      , instance.upstreamRequestId)
    self.assertNotEqual(upstream.khaleesiGate   , instance.upstreamRequestKhaleesiGate)
    self.assertNotEqual(upstream.khaleesiService, instance.upstreamRequestKhaleesiService)
    self.assertNotEqual(upstream.grpcService    , instance.upstreamRequestGrpcService)
    self.assertNotEqual(upstream.grpcMethod     , instance.upstreamRequestGrpcMethod)
    self.assertNotEqual(upstream.podId          , instance.upstreamRequestPodId)

  @patch('microservice.models.logs.grpcRequest.Model.khaleesiSave')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.metadataFromGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.responseMetadataFromGrpc')
  def testKhaleesiSaveNewEmpty(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test saving a new instance."""
    # Prepare data.
    instance = GrpcRequest()
    instance._state.adding = True  # pylint: disable=protected-access
    # Execute test.
    instance.khaleesiSave(grpc = GrpcGrpcRequest())
    # Assert result.
    parent.assert_called_once()
    metadata.assert_called_once()
    responseMetadata.assert_called_once()

  @patch('microservice.models.logs.grpcRequest.Model.toGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.metadataToGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.responseMetadataToGrpc')
  def testToGrpc(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test that general mapping to gRPC works."""
    # Prepare data.
    instance = GrpcRequest(
    upstreamRequestId              = 'upstream-request-id',
    upstreamRequestKhaleesiGate    = 'upstream-khaleesi-gate',
    upstreamRequestKhaleesiService = 'upstream-khaleesi-service',
    upstreamRequestGrpcService     = 'upstream-grpc-service',
    upstreamRequestGrpcMethod      = 'upstream-grpc-method',
    upstreamRequestPodId           = 'upstream-pod-id',
    )
    # Execute test.
    grpc = instance.toGrpc()
    # Assert result.
    metadata.assert_called_once()
    parent.assert_called_once()
    responseMetadata.assert_called_once()
    upstream = grpc.request.upstreamRequest
    self.assertEqual(instance.upstreamRequestId             , upstream.requestId)
    self.assertEqual(instance.upstreamRequestKhaleesiGate   , upstream.khaleesiGate)
    self.assertEqual(instance.upstreamRequestKhaleesiService, upstream.khaleesiService)
    self.assertEqual(instance.upstreamRequestGrpcService    , upstream.grpcService)
    self.assertEqual(instance.upstreamRequestGrpcMethod     , upstream.grpcMethod)
    self.assertEqual(instance.upstreamRequestPodId          , upstream.podId)


  @patch('microservice.models.logs.grpcRequest.Model.toGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.metadataToGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.responseMetadataToGrpc')
  def testEmptyToGrpc(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test that mapping to gRPC for empty requests works."""
    # Prepare data.
    instance = GrpcRequest()
    # Execute test.
    grpc = instance.toGrpc()
    # Assert result.
    metadata.assert_called_once()
    parent.assert_called_once()
    responseMetadata.assert_called_once()
    self.assertIsNotNone(grpc)

  def testToObjectMetadata(self) -> None :
    """Test getting the object metadata."""
    # Prepare data.
    instance = GrpcRequest()
    instance.metaCallerGrpcRequestId = 'request-id'
    # Execute test.
    result = instance.toObjectMetadata()
    # Assert result.
    self.assertEqual(instance.metaCallerGrpcRequestId, result.id)

  def _createGrpcGrpcRequest(self) -> GrpcGrpcRequest :
    """Helper to create gRPC objects."""
    grpc = GrpcGrpcRequest()

    grpc.request.upstreamRequest.requestId       = 'upstream-request-id'
    grpc.request.upstreamRequest.khaleesiGate    = 'upstream-khaleesi-gate'
    grpc.request.upstreamRequest.khaleesiService = 'upstream-khaleesi-service'
    grpc.request.upstreamRequest.grpcService     = 'upstream-grpc-service'
    grpc.request.upstreamRequest.grpcMethod      = 'upstream-grpc-method'
    grpc.request.upstreamRequest.podId           = 'upstream-pod-id'

    return grpc
