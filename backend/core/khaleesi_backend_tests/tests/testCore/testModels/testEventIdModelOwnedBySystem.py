"""Test the khaleesi base model event sending."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User, ObjectMetadata, RequestMetadata
from tests.models.eventIdModelOwnedBySystem import EventSystemModel


@patch('khaleesi.core.models.eventIdModelOwnedBySystem.SINGLETON')
class ModelManagerTestCase(SimpleTestCase):
  """Test the khaleesi base model event sending."""

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModelManager.khaleesiCreate')
  def testKhaleesiCreate(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    self._mockInstance(parent = parent)
    # Execute test.
    EventSystemModel.objects.khaleesiCreate(grpc = ObjectMetadata())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModelManager.khaleesiCreate')
  def testKhaleesiCreateError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    parent.side_effect = Exception()
    # Execute test.
    with self.assertRaises(Exception):
      EventSystemModel.objects.khaleesiCreate(grpc = ObjectMetadata())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModelManager.khaleesiUpdate')
  def testKhaleesiUpdate(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    self._mockInstance(parent = parent)
    # Execute test.
    EventSystemModel.objects.khaleesiUpdate(metadata = ObjectMetadata(), grpc = ObjectMetadata())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModelManager.khaleesiUpdate')
  def testKhaleesiUpdateError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    parent.side_effect = Exception()
    # Execute test.
    with self.assertRaises(Exception):
      EventSystemModel.objects.khaleesiUpdate(metadata = ObjectMetadata(), grpc = ObjectMetadata())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModelManager.khaleesiDelete')
  def testKhaleesiDelete(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    self._mockInstance(parent = parent)
    # Execute test.
    EventSystemModel.objects.khaleesiDelete(metadata = ObjectMetadata())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModelManager.khaleesiDelete')
  def testKhaleesiDeleteError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test creating an instance."""
    # Prepare data.
    parent.side_effect = Exception()
    # Execute test.
    with self.assertRaises(Exception):
      EventSystemModel.objects.khaleesiDelete(metadata = ObjectMetadata())
    # Assert result.
    singleton.structuredLogger.logEvent.assert_called_once()

  def _mockInstance(self, *, parent: MagicMock) -> None :
    """Mock an instance."""
    instance = MagicMock()
    instance.khaleesiId       = 'khaleesi-id'
    instance.khaleesiCreated  = datetime.now(tz = timezone.utc)
    instance.khaleesiModified = datetime.now(tz = timezone.utc)
    instance.getKhaleesiOwner.return_value = User()
    parent.return_value = instance


class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model event sending."""

  def testGetDefaultKhaleesiOwner(self) -> None :
    """Test getting the default owner."""
    # Execute test.
    owner = EventSystemModel.getDefaultKhaleesiOwner(metadata = MagicMock(), grpc = MagicMock())
    # Assert result.
    self.assertEqual(User.UserType.SYSTEM         , owner.type)
    self.assertEqual('core-khaleesi_backend_tests', owner.id)

  def testKhaleesiOwner(self) -> None :
    """Test getting the instance owner."""
    # Execute test.
    owner = EventSystemModel().getKhaleesiOwner()
    # Assert result.
    self.assertEqual(User.UserType.SYSTEM         , owner.type)
    self.assertEqual('core-khaleesi_backend_tests', owner.id)

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
        instance = EventSystemModel()
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
          instance = EventSystemModel()
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
          instance = EventSystemModel()
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
