"""Test the khaleesi base model."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from uuid import UUID

# Django.
from django.core.exceptions import ObjectDoesNotExist

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.core.shared.exceptions import DbObjectNotFoundException
from khaleesi.proto.core_pb2 import ObjectMetadata
from tests.models.idModel import IdModel


class ModelManagerTestCase(SimpleTestCase):
  """Test the khaleesi base model manager."""

  @patch.object(IdModel.objects, 'get')
  def testKhaleesiGet(self, manager: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test.
    IdModel.objects.khaleesiGet(metadata = MagicMock())
    # Assert result.
    manager.assert_called_once()

  @patch.object(IdModel.objects, 'get', side_effect = ObjectDoesNotExist())
  def testKhaleesiGetNoResult(self, *_: MagicMock) -> None :
    """Test getting an instance."""
    # Execute test & assert result..
    with self.assertRaises(DbObjectNotFoundException):
      IdModel.objects.khaleesiGet(metadata = MagicMock())

  @patch('khaleesi.core.models.idModel.BaseModelManager.khaleesiInstantiateNewInstance')
  def testKhaleesiInstantiateNewInstance(self, parent: MagicMock) -> None :
    """Test assigning the ID model attributes to new instances."""
    # Execute test.
    instance = IdModel.objects.khaleesiInstantiateNewInstance()
    # Assert result.
    self.assertTrue(UUID(instance.khaleesiId, version = 4))
    parent.assert_called_once()


class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model."""

  def testToGrpc(self) -> None :
    """Test setting the object metadata."""
    # Prepare data.
    instance = IdModel()
    instance.khaleesiId       = 'id'
    instance.khaleesiCreated  = datetime.now(tz = timezone.utc)
    instance.khaleesiModified = datetime.now(tz = timezone.utc)
    result = ObjectMetadata()
    # Execute test.
    instance.toGrpc(metadata = result)
    # Assert result.
    self.assertEqual(instance.khaleesiId      , result.id)
    self.assertEqual(
      instance.khaleesiCreated,
      result.created.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      instance.khaleesiModified,
      result.modified.ToDatetime().replace(tzinfo = timezone.utc),
    )
