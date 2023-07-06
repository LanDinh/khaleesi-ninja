"""Test the khaleesi base model."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from uuid import UUID

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata, User, RequestMetadata
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

  def testFromGrpcForCreation(self) -> None :
    """Test setting from gRPC data."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        userId = 'id'
        request = RequestMetadata()
        request.user.id   = userId
        request.user.type = userType
        STATE.reset()
        STATE.copyFrom(request = request, queries = [])
        instance = IdModel()
        # Execute test.
        instance.fromGrpc(grpc = MagicMock())
        # Assert result.
        self.assertEqual(userId   , instance.khaleesiCreatedById)
        self.assertEqual(userLabel, instance.khaleesiCreatedByType)
        self.assertEqual(userId   , instance.khaleesiModifiedById)
        self.assertEqual(userLabel, instance.khaleesiModifiedByType)

  def testFromGrpcForUpdate(self) -> None :
    """Test setting from gRPC data."""
    for creatorLabel, _ in User.UserType.items():
      for modifierLabel, modifierType in User.UserType.items():
        with self.subTest(creator = creatorLabel, modifier = modifierLabel):
          # Prepare data.
          userId = 'id'
          request = RequestMetadata()
          request.user.id   = userId
          request.user.type = modifierType
          STATE.reset()
          STATE.copyFrom(request = request, queries = [])
          instance = IdModel()
          instance.pk = 1337
          instance.khaleesiCreatedById = 'creator'
          instance.khaleesiModifiedByType = creatorLabel
          # Execute test.
          instance.fromGrpc(grpc = MagicMock())
          # Assert result.
          self.assertNotEqual(userId       , instance.khaleesiCreatedById)
          self.assertNotEqual(modifierLabel, instance.khaleesiCreatedByType)
          self.assertEqual(userId       , instance.khaleesiModifiedById)
          self.assertEqual(modifierLabel, instance.khaleesiModifiedByType)

  def testToGrpc(self) -> None :
    """Test getting gRPC data."""
    for creatorLabel, creatorType in User.UserType.items():
      for modifierLabel, modifierType in User.UserType.items():
        with self.subTest(creator = creatorLabel, modifier = modifierLabel):
          # Prepare data.
          instance = IdModel()
          instance.khaleesiId       = 'id'
          instance.khaleesiCreated       = datetime.now(tz = timezone.utc)
          instance.khaleesiCreatedById   = 'creator'
          instance.khaleesiCreatedByType = creatorLabel
          instance.khaleesiModified = datetime.now(tz = timezone.utc)
          instance.khaleesiModifiedById   = 'modifier'
          instance.khaleesiModifiedByType = modifierLabel
          result = ObjectMetadata()
          # Execute test.
          instance.toGrpc(metadata = result)
          # Assert result.
          self.assertEqual(instance.khaleesiId      , result.id)
          self.assertEqual(
            instance.khaleesiCreated,
            result.created.ToDatetime().replace(tzinfo = timezone.utc),
          )
          self.assertEqual(instance.khaleesiCreatedById, result.createdBy.id)
          self.assertEqual(creatorType                 , result.createdBy.type)
          self.assertEqual(
            instance.khaleesiModified,
            result.modified.ToDatetime().replace(tzinfo = timezone.utc),
          )
          self.assertEqual(instance.khaleesiModifiedById, result.modifiedBy.id)
          self.assertEqual(modifierType                 , result.modifiedBy.type)
