"""Test the khaleesi base model event sending."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from tests.models.eventIdModelOwnedBySystem import EventSystemModel


class ModelTestCase(SimpleTestCase):
  """Test the khaleesi base model event sending."""

  def testKhaleesiOwner(self) -> None :
    """Test getting the instance owner."""
    # Execute test.
    owner = EventSystemModel().khaleesiOwner
    # Assert result.
    self.assertEqual(User.UserType.SYSTEM         , owner.type)
    self.assertEqual('core-khaleesi_backend_tests', owner.id)

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.SINGLETON')
  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModel.khaleesiSave')
  def testKhaleesiSaveNew(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test setting from gRPC data."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        parent.reset_mock()
        singleton.reset_mock()
        userId = 'id'
        request = RequestMetadata()
        request.user.id   = userId
        request.user.type = userType
        STATE.reset()
        STATE.copyFrom(request = request, queries = [])
        instance = EventSystemModel()
        instance._state.adding = True  # pylint: disable=protected-access
        # Execute test.
        instance.khaleesiSave(grpc = MagicMock())
        # Assert result.
        parent.assert_called_once()
        singleton.structuredLogger.logEvent.assert_called_once()
        self.assertEqual(userId   , instance.khaleesiCreatedById)
        self.assertEqual(userLabel, instance.khaleesiCreatedByType)
        self.assertEqual(userId   , instance.khaleesiModifiedById)
        self.assertEqual(userLabel, instance.khaleesiModifiedByType)

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.SINGLETON')
  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModel.khaleesiSave')
  def testKhaleesiSaveOld(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test setting from gRPC data."""
    singleton.reset_mock()
    for creatorLabel, creatorType in User.UserType.items():
      for modifierLabel, modifierType in [
          (modifierLabel, modifierType) for modifierLabel, modifierType
          in User.UserType.items() if creatorType != modifierType ]:
        with self.subTest(creator = creatorLabel, modifier = modifierLabel):
          # Prepare data.
          parent.reset_mock()
          singleton.reset_mock()
          userId = 'id'
          request = RequestMetadata()
          request.user.id   = userId
          request.user.type = modifierType
          STATE.reset()
          STATE.copyFrom(request = request, queries = [])
          instance = EventSystemModel()
          instance.khaleesiCreatedById   = 'creator'
          instance.khaleesiCreatedByType = creatorLabel
          instance._state.adding         = False  # pylint: disable=protected-access
          # Execute test.
          instance.khaleesiSave(grpc = MagicMock())
          # Assert result.
          parent.assert_called_once()
          singleton.structuredLogger.logEvent.assert_called_once()
          self.assertNotEqual(userId       , instance.khaleesiCreatedById)
          self.assertNotEqual(modifierLabel, instance.khaleesiCreatedByType)
          self.assertEqual(userId       , instance.khaleesiModifiedById)
          self.assertEqual(modifierLabel, instance.khaleesiModifiedByType)

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.SINGLETON')
  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModel.khaleesiSave')
  def testKhaleesiSaveError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test setting from gRPC data."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        parent.reset_mock()
        parent.side_effect = Exception()
        singleton.reset_mock()
        userId = 'id'
        request = RequestMetadata()
        request.user.id   = userId
        request.user.type = userType
        STATE.reset()
        STATE.copyFrom(request = request, queries = [])
        instance = EventSystemModel()
        instance._state.adding = True  # pylint: disable=protected-access
        # Execute test.
        with self.assertRaises(Exception):
          instance.khaleesiSave(grpc = MagicMock())
        # Assert result.
        parent.assert_called_once()
        singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.SINGLETON')
  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModel.delete')
  def testDelete(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test deletion."""
    # Prepare data.
    instance = EventSystemModel()
    # Execute test.
    instance.delete()
    # Assert result.
    parent.assert_called_once()
    singleton.structuredLogger.logEvent.assert_called_once()

  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.SINGLETON')
  @patch('khaleesi.core.models.eventIdModelOwnedBySystem.BaseModel.delete')
  def testDeleteError(self, parent: MagicMock, singleton: MagicMock) -> None :
    """Test deletion."""
    # Prepare data.
    instance = EventSystemModel()
    parent.side_effect = Exception()
    # Execute test.
    with self.assertRaises(Exception):
      instance.delete()
    # Assert result.
    parent.assert_called_once()
    singleton.structuredLogger.logEvent.assert_called_once()

  def testToObjectMetadata(self) -> None :
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
          # Execute test.
          result = instance.toObjectMetadata()
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
