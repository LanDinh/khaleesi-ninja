"""Test the khaleesi base model."""

# Python.
from unittest.mock import patch, MagicMock
from uuid import UUID

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models.idModel import IdModel


class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model."""

  @patch('khaleesi.core.models.idModel.BaseModel.khaleesiSave')
  def testKhaleesiSaveNew(self, parent: MagicMock) -> None :
    """Test setting from gRPC data."""
    # Prepare data.
    oldId = 'old-id'
    instance               = IdModel()
    instance._state.adding = True  # pylint: disable=protected-access
    instance.khaleesiId    = oldId
    # Execute test.
    instance.khaleesiSave(grpc = MagicMock())
    # Assert result.
    parent.assert_called_once()
    self.assertNotEqual(oldId, instance.khaleesiId)
    self.assertTrue(UUID(instance.khaleesiId))

  @patch('khaleesi.core.models.idModel.BaseModel.khaleesiSave')
  def testKhaleesiSaveOld(self, parent: MagicMock) -> None :
    """Test setting from gRPC data."""
    # Prepare data.
    oldId = 'old-id'
    instance               = IdModel()
    instance._state.adding = False  # pylint: disable=protected-access
    instance.khaleesiId    = oldId
    # Execute test.
    instance.khaleesiSave(grpc = MagicMock())
    # Assert result.
    parent.assert_called_once()
    self.assertEqual(oldId, instance.khaleesiId)

  @patch('khaleesi.core.models.idModel.BaseModel.toGrpc')
  def testToGrpc(self, parent: MagicMock) -> None :
    """Test getting gRPC data."""
    # Prepare data.
    instance = IdModel()
    instance.khaleesiId = 'id'
    result = ObjectMetadata()
    # Execute test.
    instance.toGrpc(metadata = result)
    # Assert result.
    parent.assert_called_once()
    self.assertEqual(instance.khaleesiId, result.id)
