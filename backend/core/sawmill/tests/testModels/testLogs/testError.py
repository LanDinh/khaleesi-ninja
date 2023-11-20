"""Test the error logs."""

# Python.
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import ErrorRequest as GrpcErrorRequest
from microservice.models import Error


class ErrorTestCase(SimpleTestCase):
  """Test the error logs models."""

  @patch('microservice.models.logs.error.parseString')
  @patch('microservice.models.logs.error.Model.khaleesiSave')
  @patch('microservice.models.logs.error.Error.metadataFromGrpc')
  def testKhaleesiSaveNew(
      self,
      metadata: MagicMock,
      parent  : MagicMock,
      string  : MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    string.return_value = 'parsed-string'
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          metadata.reset_mock()
          parent.reset_mock()
          instance               = Error()
          instance._state.adding = True  # pylint: disable=protected-access
          grpc = self._createGrpcError(status = status, loglevel = loglevel)
          # Execute test.
          instance.khaleesiSave(grpc = grpc)
          # Assert result.
          metadata.assert_called_once()
          parent.assert_called_once()
          self.assertEqual(grpc.error.publicDetails , instance.publicDetails)
          self.assertEqual(grpc.error.privateMessage, instance.privateMessage)
          self.assertEqual(grpc.error.privateDetails, instance.privateDetails)
          self.assertEqual(grpc.error.stacktrace    , instance.stacktrace)

  @patch('microservice.models.logs.error.parseString')
  @patch('microservice.models.logs.error.Model.khaleesiSave')
  @patch('microservice.models.logs.error.Error.metadataFromGrpc')
  def testKhaleesiSaveOld(
      self,
      metadata: MagicMock,
      parent  : MagicMock,
      string  : MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    string.return_value = 'parsed-string'
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare data.
          metadata.reset_mock()
          parent.reset_mock()
          instance               = Error()
          instance._state.adding = False  # pylint: disable=protected-access
          grpc = self._createGrpcError(status = status, loglevel = loglevel)
          # Execute test.
          instance.khaleesiSave(grpc = grpc)
          # Assert result.
          metadata.assert_called_once()
          parent.assert_called_once()
          self.assertNotEqual(grpc.error.publicDetails , instance.publicDetails)
          self.assertNotEqual(grpc.error.privateMessage, instance.privateMessage)
          self.assertNotEqual(grpc.error.privateDetails, instance.privateDetails)
          self.assertNotEqual(grpc.error.stacktrace    , instance.stacktrace)

  @patch('microservice.models.logs.error.parseString')
  @patch('microservice.models.logs.error.Model.khaleesiSave')
  @patch('microservice.models.logs.error.Error.metadataFromGrpc')
  def testKhaleesiSaveNewEmpty(
      self,
      metadata: MagicMock,
      parent  : MagicMock,
      string  : MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    # Prepare data.
    string.return_value = 'parsed-string'
    instance               = Error()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = GrpcErrorRequest()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    metadata.assert_called_once()
    parent.assert_called_once()

  @patch('microservice.models.logs.error.Error.toObjectMetadata')
  @patch('microservice.models.logs.error.Error.metadataToGrpc')
  def testToGrpc(self, metadata: MagicMock, objectMetadata: MagicMock) -> None :
    """Test that general mapping to gRPC works."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name):
          # Prepare data.
          metadata.reset_mock()
          objectMetadata.reset_mock()
          objectMetadata.return_value = ObjectMetadata()
          instance = Error(
            status         = status.name,
            loglevel       = loglevel.name,
            site           = 'site',
            app            = 'app',
            publicKey      = 'public-key',
            publicDetails  = 'public-details',
            privateMessage = 'private-message',
            privateDetails = 'private-details',
            stacktrace     = 'stacktrace',
          )
          # Execute test.
          result = instance.toGrpc()
          # Assert result.
          metadata.assert_called_once()
          objectMetadata.assert_called_once()
          self.assertEqual(instance.status        , result.error.status)
          self.assertEqual(instance.loglevel      , result.error.loglevel)
          self.assertEqual(instance.site          , result.error.site)
          self.assertEqual(instance.app           , result.error.app)
          self.assertEqual(instance.publicKey     , result.error.publicKey)
          self.assertEqual(instance.publicDetails , result.error.publicDetails)
          self.assertEqual(instance.privateMessage, result.error.privateMessage)
          self.assertEqual(instance.privateDetails, result.error.privateDetails)
          self.assertEqual(instance.stacktrace    , result.error.stacktrace)

  @patch('microservice.models.logs.error.Error.toObjectMetadata')
  @patch('microservice.models.logs.error.Error.metadataToGrpc')
  def testToGrpcEmpty(self, metadata: MagicMock, objectMetadata: MagicMock) -> None :
    """Test that mapping to gRPC for empty errors works."""
    # Prepare data.
    error = Error()
    objectMetadata.return_value = ObjectMetadata()
    # Execute test.
    error.toGrpc()
    # Assert result.
    metadata.assert_called_once()
    objectMetadata.assert_called_once()

  def _createGrpcError(self, *, status: StatusCode, loglevel: LogLevel) -> GrpcErrorRequest :
    """Utility method for creating gRPC Errors."""
    grpc = GrpcErrorRequest()

    grpc.error.status         = status.name
    grpc.error.loglevel       = loglevel.name
    grpc.error.site           = 'site'
    grpc.error.app            = 'app'
    grpc.error.publicKey      = 'public-key'
    grpc.error.publicDetails  = 'public-details'
    grpc.error.privateMessage = 'private-message'
    grpc.error.privateDetails = 'private-details'
    grpc.error.stacktrace     = 'stacktrace'

    return grpc
