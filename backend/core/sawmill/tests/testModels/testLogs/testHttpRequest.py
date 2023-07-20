"""Test the HTTP request logs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_sawmill_pb2 import HttpRequestRequest as GrpcHttpRequest
from microservice.models import HttpRequest


class HttpRequestTestCase(SimpleTestCase):
  """Test the HTTP request logs models."""

  @patch('microservice.models.logs.httpRequest.Model.khaleesiSave')
  @patch('microservice.models.logs.httpRequest.HttpRequest.metadataFromGrpc')
  @patch('microservice.models.logs.httpRequest.HttpRequest.responseMetadataFromGrpc')
  def testKhaleesiSaveNew(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test saving a new instance."""
    # Prepare data.
    instance = HttpRequest()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = self._createGrpcHttpRequest()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    metadata.assert_called_once()
    responseMetadata.assert_called_once()
    self.assertEqual(grpc.request.language      , instance.language)
    self.assertEqual(grpc.request.deviceId      , instance.deviceId)
    self.assertEqual(grpc.request.languageHeader, instance.languageHeader)
    self.assertEqual(grpc.request.ip            , instance.ip)
    self.assertEqual(grpc.request.useragent     , instance.useragent)

  @patch('microservice.models.logs.httpRequest.Model.khaleesiSave')
  @patch('microservice.models.logs.httpRequest.HttpRequest.metadataFromGrpc')
  @patch('microservice.models.logs.httpRequest.HttpRequest.responseMetadataFromGrpc')
  def testKhaleesiSaveOld(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test saving an old instance."""
    # Prepare data.
    instance = HttpRequest()
    instance._state.adding = False  # pylint: disable=protected-access
    grpc = self._createGrpcHttpRequest()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    metadata.assert_called_once()
    responseMetadata.assert_called_once()
    self.assertNotEqual(grpc.request.language      , instance.language)
    self.assertNotEqual(grpc.request.deviceId      , instance.deviceId)
    self.assertNotEqual(grpc.request.languageHeader, instance.languageHeader)
    self.assertNotEqual(grpc.request.ip            , instance.ip)
    self.assertNotEqual(grpc.request.useragent     , instance.useragent)

  @patch('microservice.models.logs.httpRequest.Model.khaleesiSave')
  @patch('microservice.models.logs.httpRequest.HttpRequest.metadataFromGrpc')
  @patch('microservice.models.logs.httpRequest.HttpRequest.responseMetadataFromGrpc')
  def testKhaleesiSaveNewEmpty(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test saving a new instance."""
    # Prepare data.
    instance = HttpRequest()
    instance._state.adding = True  # pylint: disable=protected-access
    # Execute test.
    instance.khaleesiSave(grpc = GrpcHttpRequest())
    # Assert result.
    parent.assert_called_once()
    metadata.assert_called_once()
    responseMetadata.assert_called_once()

  @patch('microservice.models.logs.httpRequest.Model.toGrpc')
  @patch('microservice.models.logs.httpRequest.HttpRequest.metadataToGrpc')
  @patch('microservice.models.logs.httpRequest.HttpRequest.responseMetadataToGrpc')
  def testToGrpc(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test that general mapping to gRPC works."""
    # Prepare data.
    instance = HttpRequest(
      language       = 'language',
      deviceId       = 'device-id',
      languageHeader = 'language-header',
      ip             = 'ip',
      useragent      = 'useragent',
      geolocation    = 'geolocation',
      browser        = 'browser',
      renderingAgent = 'rendering-agent',
      os             = 'os',
      deviceType     = 'device-type',
    )
    # Execute test.
    grpc = instance.toGrpc()
    # Assert result.
    metadata.assert_called_once()
    parent.assert_called_once()
    responseMetadata.assert_called_once()
    self.assertEqual(instance.language      , grpc.request.language)
    self.assertEqual(instance.deviceId      , grpc.request.deviceId)
    self.assertEqual(instance.languageHeader, grpc.request.languageHeader)
    self.assertEqual(instance.ip            , grpc.request.ip)
    self.assertEqual(instance.useragent     , grpc.request.useragent)
    self.assertEqual(instance.geolocation   , grpc.request.geolocation)
    self.assertEqual(instance.browser       , grpc.request.browser)
    self.assertEqual(instance.renderingAgent, grpc.request.renderingAgent)
    self.assertEqual(instance.os            , grpc.request.os)
    self.assertEqual(instance.deviceType    , grpc.request.deviceType)


  @patch('microservice.models.logs.httpRequest.Model.toGrpc')
  @patch('microservice.models.logs.httpRequest.HttpRequest.metadataToGrpc')
  @patch('microservice.models.logs.httpRequest.HttpRequest.responseMetadataToGrpc')
  def testEmptyToGrpc(
      self,
      responseMetadata: MagicMock,
      metadata        : MagicMock,
      parent          : MagicMock,
  ) -> None :
    """Test that mapping to gRPC for empty requests works."""
    # Prepare data.
    instance = HttpRequest()
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
    instance = HttpRequest()
    instance.metaCallerHttpRequestId = 'request-id'
    # Execute test.
    result = instance.toObjectMetadata()
    # Assert result.
    self.assertEqual(instance.metaCallerHttpRequestId, result.id)

  def _createGrpcHttpRequest(self) -> GrpcHttpRequest :
    """Helper to create gRPC objects."""
    grpc = GrpcHttpRequest()

    grpc.request.language       = 'language'
    grpc.request.deviceId       = 'device-id'
    grpc.request.languageHeader = 'language-header'
    grpc.request.ip             = 'ip'
    grpc.request.useragent      = 'useragent'

    return grpc
