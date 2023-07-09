"""Test the khaleesi base model."""

# Python.
from unittest.mock import patch, MagicMock
from uuid import UUID

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models.idModel import IdModel


class ModelManagerTestCase(SimpleTestCase):
  """Test the khaleesi base model manager."""

  @patch.object(IdModel.objects, 'get')
  def testBaseKhaleesiGet(self, manager: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test.
    IdModel.objects.khaleesiGet(metadata = MagicMock())
    # Assert result.
    manager.assert_called_once()


class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model."""

  def testFromGrpcForCreation(self) -> None :
    """Test setting from gRPC data."""
    # Prepare data.
    instance = IdModel()
    # Execute test.
    instance.fromGrpc(grpc = MagicMock())
    # Assert result.
    self.assertTrue(UUID(instance.khaleesiId))

  def testFromGrpcForUpdate(self) -> None :
    """Test setting from gRPC data."""
    # Prepare data.
    instance = IdModel()
    instance.pk = 1337
    # Execute test.
    instance.fromGrpc(grpc = MagicMock())
    # Assert result.
    with self.assertRaises(ValueError):
      UUID(instance.khaleesiId)

  def testToGrpc(self) -> None :
    """Test getting gRPC data."""
    # Prepare data.
    instance = IdModel()
    instance.khaleesiId = 'id'
    result = ObjectMetadata()
    # Execute test.
    instance.toGrpc(metadata = result)
    # Assert result.
    self.assertEqual(instance.khaleesiId, result.id)
