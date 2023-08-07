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
    self.assertEqual(upstream.requestId, instance.upstreamRequestId)
    self.assertEqual(upstream.site     , instance.upstreamRequestSite)
    self.assertEqual(upstream.app      , instance.upstreamRequestApp)
    self.assertEqual(upstream.service  , instance.upstreamRequestService)
    self.assertEqual(upstream.method   , instance.upstreamRequestMethod)
    self.assertEqual(upstream.podId    , instance.upstreamRequestPodId)

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
    self.assertNotEqual(upstream.requestId, instance.upstreamRequestId)
    self.assertNotEqual(upstream.site     , instance.upstreamRequestSite)
    self.assertNotEqual(upstream.app      , instance.upstreamRequestApp)
    self.assertNotEqual(upstream.service  , instance.upstreamRequestService)
    self.assertNotEqual(upstream.method   , instance.upstreamRequestMethod)
    self.assertNotEqual(upstream.podId    , instance.upstreamRequestPodId)

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

  @patch('microservice.models.logs.grpcRequest.GrpcRequest.metadataToGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.responseMetadataToGrpc')
  def testToGrpc(self, responseMetadata: MagicMock, metadata: MagicMock) -> None :
    """Test that general mapping to gRPC works."""
    # Prepare data.
    instance = GrpcRequest(
    upstreamRequestId      = 'upstream-request-id',
    upstreamRequestSite    = 'upstream-site',
    upstreamRequestApp     = 'upstream-app',
    upstreamRequestService = 'upstream-service',
    upstreamRequestMethod  = 'upstream-method',
    upstreamRequestPodId   = 'upstream-pod-id',
    )
    # Execute test.
    grpc = instance.toGrpc()
    # Assert result.
    metadata.assert_called_once()
    responseMetadata.assert_called_once()
    upstream = grpc.request.upstreamRequest
    self.assertEqual(instance.upstreamRequestId     , upstream.requestId)
    self.assertEqual(instance.upstreamRequestSite   , upstream.site)
    self.assertEqual(instance.upstreamRequestApp    , upstream.app)
    self.assertEqual(instance.upstreamRequestService, upstream.service)
    self.assertEqual(instance.upstreamRequestMethod , upstream.method)
    self.assertEqual(instance.upstreamRequestPodId  , upstream.podId)


  @patch('microservice.models.logs.grpcRequest.GrpcRequest.metadataToGrpc')
  @patch('microservice.models.logs.grpcRequest.GrpcRequest.responseMetadataToGrpc')
  def testToGrpcEmpty(self, responseMetadata: MagicMock, metadata: MagicMock) -> None :
    """Test that mapping to gRPC for empty requests works."""
    # Prepare data.
    instance = GrpcRequest()
    # Execute test.
    grpc = instance.toGrpc()
    # Assert result.
    metadata.assert_called_once()
    responseMetadata.assert_called_once()
    self.assertIsNotNone(grpc)

  @patch('microservice.models.logs.grpcRequest.Model.toObjectMetadata')
  def testToObjectMetadata(self, parent: MagicMock) -> None :
    """Test getting the object metadata."""
    # Prepare data.
    instance = GrpcRequest()
    instance.metaCallerGrpcRequestId = 'request-id'
    # Execute test.
    result = instance.toObjectMetadata()
    # Assert result.
    parent.assert_called_once()
    self.assertEqual(instance.metaCallerGrpcRequestId, result.id)

  def _createGrpcGrpcRequest(self) -> GrpcGrpcRequest :
    """Helper to create gRPC objects."""
    grpc = GrpcGrpcRequest()

    grpc.request.upstreamRequest.requestId = 'upstream-request-id'
    grpc.request.upstreamRequest.site      = 'upstream-site'
    grpc.request.upstreamRequest.app       = 'upstream-app'
    grpc.request.upstreamRequest.service   = 'upstream-service'
    grpc.request.upstreamRequest.method    = 'upstream-method'
    grpc.request.upstreamRequest.podId     = 'upstream-pod-id'

    return grpc
