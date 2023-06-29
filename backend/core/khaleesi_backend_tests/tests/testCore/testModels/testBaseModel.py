"""Test the khaleesi base model."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Django.
from django.core.exceptions import ObjectDoesNotExist

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.core.shared.exceptions import (
  DbObjectNotFoundException,
  DbOutdatedInformationException,
  DbObjectTwinException,
)
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models import Model, Grpc


class ModelManagerTestCase(SimpleTestCase):
  """Test the khaleesi base model manager."""

  @patch('khaleesi.core.models.baseModel.transaction.atomic')
  @patch.object(Model.objects, 'filter')
  def testKhaleesiCreate(self, *_: MagicMock) -> None :
    """Test creating an instance."""
    # Execute test.
    result = Model.objects.khaleesiCreate(grpc = MagicMock())
    # Assert result.
    self.assertEqual(1, result.khaleesiVersion)
    self.assertIsNotNone(result.khaleesiId)
    self.assertTrue(result.saved)  # type: ignore[attr-defined]

  @patch('khaleesi.core.models.baseModel.transaction.atomic')
  @patch.object(Model.objects, 'filter', return_value = [ 'one', 'two' ])
  def testKhaleesiCreateNotBecauseDupe(self, *_: MagicMock) -> None :
    """Test creating an instance."""
    # Execute test & assert result.
    with self.assertRaises(DbObjectTwinException):
      Model.objects.khaleesiCreate(grpc = MagicMock())

  @patch('khaleesi.core.models.baseModel.transaction.atomic')
  @patch.object(Model.objects, 'get')
  def testKhaleesiUpdate(self, manager: MagicMock, *_: MagicMock) -> None :
    """Test updating an instance."""
    # Prepare data.
    metadata = ObjectMetadata()
    metadata.version = 1337
    instance = MagicMock()
    instance.khaleesiVersion = 1337
    manager.return_value = instance
    # Execute test.
    result = Model.objects.khaleesiUpdate(metadata = metadata, grpc = Grpc())  # type: ignore[arg-type]  # pylint: disable=line-too-long
    # Assert result.
    result.save.assert_called_once()  # type: ignore[attr-defined]
    self.assertEqual(metadata.version + 1, result.khaleesiVersion)

  @patch('khaleesi.core.models.baseModel.transaction')
  @patch.object(Model.objects, 'get')
  def testKhaleesiUpdateVersionMismatch(self, manager: MagicMock, *_: MagicMock) -> None :
    """Test updating an instance."""
    # Prepare data.
    instance = MagicMock()
    instance.khaleesiVersion = 1337
    manager.return_value = instance
    # Execute test & assert result.
    with self.assertRaises(DbOutdatedInformationException):
      Model.objects.khaleesiUpdate(metadata = MagicMock(), grpc = Grpc())  # type: ignore[arg-type]

  @patch.object(Model.objects, 'filter')
  def testKhaleesiDelete(self, manager: MagicMock) -> None :
    """Test deleting an instance."""
    # Execute test.
    Model.objects.khaleesiDelete(metadata = MagicMock())
    # Assert result.
    manager.return_value.delete.assert_called_once()

  @patch.object(Model.objects, 'get')
  def testKhaleesiGet(self, manager: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test.
    Model.objects.khaleesiGet(metadata = MagicMock())
    # Assert result.
    manager.assert_called_once()

  @patch.object(Model.objects, 'get', side_effect = ObjectDoesNotExist())
  def testKhaleesiGetNoResult(self, *_: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test & assert result..
    with self.assertRaises(DbObjectNotFoundException):
      Model.objects.khaleesiGet(metadata = MagicMock())


class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model."""

  def testModelType(self) -> None :
    """Test documenting the model type."""
    # Execute test.
    result = Model.modelType()
    # Assert result.
    self.assertEqual('tests.models.Model', result)

  def testToGrpc(self) -> None :
    """Test setting the object metadata."""
    # Prepare data.
    instance = Model()
    instance.khaleesiId       = 'id'
    instance.khaleesiVersion  = 1337
    instance.khaleesiCreated  = datetime.now(tz = timezone.utc)
    instance.khaleesiModified = datetime.now(tz = timezone.utc)
    result = ObjectMetadata()
    # Execute test.
    instance.toGrpc(metadata = result)
    # Assert result.
    self.assertEqual(instance.khaleesiId      , result.id)
    self.assertEqual(instance.khaleesiVersion , result.version)
    self.assertEqual(
      instance.khaleesiCreated,
      result.created.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      instance.khaleesiModified,
      result.modified.ToDatetime().replace(tzinfo = timezone.utc),
    )
