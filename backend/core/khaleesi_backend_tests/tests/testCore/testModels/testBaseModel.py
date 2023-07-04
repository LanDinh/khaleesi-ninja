"""Test the khaleesi base model."""

# Python.
from unittest.mock import patch, MagicMock

# Django.
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.core.shared.exceptions import (
  DbObjectNotFoundException,
  DbOutdatedInformationException,
  DbObjectTwinException,
)
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models.baseModel import BaseModel, Grpc


class ModelManagerTestCase(SimpleTestCase):
  """Test the khaleesi base model manager."""

  def testKhaleesiCreate(self) -> None :
    """Test creating an instance."""
    # Execute test.
    result = BaseModel.objects.khaleesiCreate(grpc = MagicMock())
    # Assert result.
    self.assertEqual(1, result.khaleesiVersion)
    # noinspection PyUnresolvedReferences
    self.assertTrue(result.saved)

  @patch('khaleesi.core.models.baseModel.transaction.atomic')
  @patch.object(BaseModel.objects, 'khaleesiGet')
  def testKhaleesiUpdate(self, manager: MagicMock, *_: MagicMock) -> None :
    """Test updating an instance."""
    # Prepare data.
    metadata = ObjectMetadata()
    metadata.version = 1337
    instance = MagicMock()
    instance.khaleesiVersion = 1337
    manager.return_value = instance
    # Execute test.
    result = BaseModel.objects.khaleesiUpdate(metadata = metadata, grpc = Grpc())
    # Assert result.
    result.save.assert_called_once()  # type: ignore[attr-defined]
    self.assertEqual(metadata.version + 1, result.khaleesiVersion)

  @patch('khaleesi.core.models.baseModel.transaction')
  @patch.object(BaseModel.objects, 'khaleesiGet')
  def testKhaleesiUpdateVersionMismatch(self, manager: MagicMock, *_: MagicMock) -> None :
    """Test updating an instance."""
    # Prepare data.
    instance = MagicMock()
    instance.khaleesiVersion = 1337
    manager.return_value = instance
    # Execute test & assert result.
    with self.assertRaises(DbOutdatedInformationException):
      BaseModel.objects.khaleesiUpdate(metadata = MagicMock(), grpc = Grpc())

  @patch('khaleesi.core.models.baseModel.transaction')
  @patch.object(BaseModel.objects, 'khaleesiGet')
  def testKhaleesiDelete(self, manager: MagicMock, *_: MagicMock) -> None :
    """Test deleting an instance."""
    # Execute test.
    BaseModel.objects.khaleesiDelete(metadata = MagicMock())
    # Assert result.
    manager.return_value.delete.assert_called_once()

  @patch.object(BaseModel.objects, 'baseKhaleesiGet')
  def testKhaleesiGet(self, baseGet: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test.
    BaseModel.objects.khaleesiGet(metadata = MagicMock())
    # Assert result.
    baseGet.assert_called_once()

  @patch.object(BaseModel.objects, 'baseKhaleesiGet', side_effect = MultipleObjectsReturned())
  def testKhaleesiGetNotFound(self, baseGet: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test.
    with self.assertRaises(DbObjectTwinException):
      BaseModel.objects.khaleesiGet(metadata = MagicMock())
    # Assert result.
    baseGet.assert_called_once()

  @patch.object(BaseModel.objects, 'baseKhaleesiGet', side_effect = ObjectDoesNotExist())
  def testKhaleesiGetMultipleFound(self, baseGet: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test.
    with self.assertRaises(DbObjectNotFoundException):
      BaseModel.objects.khaleesiGet(metadata = MagicMock())
    # Assert result.
    baseGet.assert_called_once()


class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model."""

  def testModelType(self) -> None :
    """Test documenting the model type."""
    # Execute test.
    result = BaseModel.modelType()
    # Assert result.
    self.assertEqual('tests.models.baseModel.BaseModel', result)

  def testToGrpc(self) -> None :
    """Test setting the object metadata."""
    # Prepare data.
    instance = BaseModel()
    instance.khaleesiVersion  = 1337
    result = ObjectMetadata()
    # Execute test.
    instance.toGrpc(metadata = result)
    # Assert result.
    self.assertEqual(instance.khaleesiVersion , result.version)
