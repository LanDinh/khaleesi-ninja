"""Test the khaleesi base model."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.core.shared.exceptions import DbOutdatedInformationException
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models.baseModel import BaseModel



class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model."""

  def testModelType(self) -> None :
    """Test documenting the model type."""
    # Execute test.
    result = BaseModel.modelType()
    # Assert result.
    self.assertEqual('tests.models.baseModel.BaseModel', result)

  @patch('khaleesi.core.models.baseModel.transaction')
  @patch('khaleesi.core.models.baseModel.Model.refresh_from_db')
  @patch('khaleesi.core.models.baseModel.Model.save')
  def testKhaleesiSave(self, parent: MagicMock, *_: MagicMock) -> None :
    """Test saving the instance."""
    for adding in [ True, False ]:
      with self.subTest(adding = adding):
        # Prepare data.
        parent.reset_mock()
        version = 1337
        instance                 = BaseModel()
        instance.khaleesiVersion = version
        instance._state.adding   = adding  # pylint: disable=protected-access
        metadata         = ObjectMetadata()
        metadata.version = version
        # Execute test.
        instance.khaleesiSave(metadata = metadata, grpc = MagicMock())
        # Assert result.
        self.assertEqual(version + 1, instance.khaleesiVersion)
        parent.assert_called_once()

  @patch('khaleesi.core.models.baseModel.transaction.atomic')
  @patch('khaleesi.core.models.baseModel.models.Model.refresh_from_db')
  @patch('khaleesi.core.models.baseModel.models.Model.save')
  def testKhaleesiSaveVersionMismatchDbRefresh(
      self,
      parent : MagicMock,
      refresh: MagicMock,
      *_     : MagicMock,
  ) -> None :
    """Test saving the instance."""
    # Prepare data.
    version = 1337
    instance                 = BaseModel()
    instance.khaleesiVersion = version
    instance._state.adding   = False  # pylint: disable=protected-access
    metadata         = ObjectMetadata()
    metadata.version = version
    def refreshFromDb() -> None :
      instance.khaleesiVersion = 9000
    refresh.side_effect = refreshFromDb
    # Execute test.
    with self.assertRaises(DbOutdatedInformationException):
      instance.khaleesiSave(metadata = metadata, grpc = MagicMock())
    # Assert result.
    parent.assert_not_called()

  @patch('khaleesi.core.models.baseModel.transaction')
  @patch('khaleesi.core.models.baseModel.models.Model.refresh_from_db')
  @patch('khaleesi.core.models.baseModel.models.Model.save')
  def testKhaleesiSaveVersionMismatchMetadata(self, parent: MagicMock, *_: MagicMock) -> None :
    """Test saving the instance."""
    # Prepare data.
    version = 1337
    instance                 = BaseModel()
    instance.khaleesiVersion = version
    instance._state.adding   = True  # pylint: disable=protected-access
    metadata         = ObjectMetadata()
    metadata.version = version - 1
    # Execute test.
    with self.assertRaises(DbOutdatedInformationException):
      instance.khaleesiSave(metadata = metadata, grpc = MagicMock())
    # Assert result.
    parent.assert_not_called()

  def testToGrpc(self) -> None :
    """Test mapping the instance to gRPC."""
    # Prepare data.
    instance = BaseModel()
    instance.khaleesiVersion  = 1337
    result = ObjectMetadata()
    # Execute test.
    instance.toGrpc(metadata = result)
    # Assert result.
    self.assertEqual(instance.khaleesiVersion , result.version)
