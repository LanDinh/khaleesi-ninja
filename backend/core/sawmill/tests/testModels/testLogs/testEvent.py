"""Test the event logs."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent, EventRequest as GrpcEventRequest
from microservice.models import Event


class EventTestCase(SimpleTestCase):
  """Test the event logs models."""

  @patch('microservice.models.logs.event.parseString')
  @patch('microservice.models.logs.event.Model.khaleesiSave')
  @patch('microservice.models.logs.event.Event.metadataFromGrpc')
  def testKhaleesiSaveNew(
      self,
      metadata: MagicMock,
      parent  : MagicMock,
      string  : MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    string.return_value = 'parsed-string'
    for actionLabel, actionType in GrpcEvent.Action.ActionType.items():
      for resultLabel, resultType in GrpcEvent.Action.ResultType.items():
        for ownerLabel, ownerType in User.UserType.items():
          with self.subTest(action = actionLabel, result = resultLabel, owner = ownerLabel):
            # Prepare data.
            metadata.reset_mock()
            parent.reset_mock()
            instance               = Event()
            instance._state.adding = True  # pylint: disable=protected-access
            grpc = self._createGrpcEvent(
              owner  = ownerType,
              action = actionType,
              result = resultType,
            )
            # Execute test.
            instance.khaleesiSave(grpc = grpc)
            # Assert result.
            metadata.assert_called_once()
            parent.assert_called_once()
            self.assertEqual(ownerLabel                  , instance.targetOwnerType)
            self.assertEqual(actionLabel                 , instance.actionCrudType)
            self.assertEqual(grpc.event.action.customType, instance.actionCustomType)
            self.assertEqual(resultLabel                 , instance.actionResult)
            self.assertEqual(grpc.event.action.details   , instance.actionDetails)

  @patch('microservice.models.logs.event.parseString')
  @patch('microservice.models.logs.event.Model.khaleesiSave')
  @patch('microservice.models.logs.event.Event.metadataFromGrpc')
  def testKhaleesiSaveOld(
      self,
      metadata: MagicMock,
      parent  : MagicMock,
      string  : MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    string.return_value = 'parsed-string'
    for actionLabel, actionType in [
        (actionLabel, actionType) for actionLabel, actionType in GrpcEvent.Action.ActionType.items()
        if actionType != GrpcEvent.Action.ActionType.UNKNOWN_ACTION
    ]:
      for resultLabel, resultType in [
          (resultLabel, resultType)
          for resultLabel, resultType in GrpcEvent.Action.ResultType.items()
          if resultType != GrpcEvent.Action.ResultType.UNKNOWN_RESULT
      ]:
        for ownerLabel, ownerType in [
            (ownerLabel, ownerType) for ownerLabel, ownerType in User.UserType.items()
            if ownerType != User.UserType.UNKNOWN
        ]:
          with self.subTest(action = actionLabel, result = resultLabel, owner = ownerLabel):
            # Prepare data.
            metadata.reset_mock()
            parent.reset_mock()
            instance               = Event()
            instance._state.adding = False  # pylint: disable=protected-access
            grpc = self._createGrpcEvent(
              owner  = ownerType,
              action = actionType,
              result = resultType,
            )
            # Execute test.
            instance.khaleesiSave(grpc = grpc)
            # Assert result.
            metadata.assert_called_once()
            parent.assert_called_once()
            self.assertNotEqual(ownerLabel                  , instance.targetOwnerType)
            self.assertNotEqual(actionLabel                 , instance.actionCrudType)
            self.assertNotEqual(grpc.event.action.customType, instance.actionCustomType)
            self.assertNotEqual(resultLabel                 , instance.actionResult)
            self.assertNotEqual(grpc.event.action.details   , instance.actionDetails)

  @patch('microservice.models.logs.event.parseString')
  @patch('microservice.models.logs.event.Model.khaleesiSave')
  @patch('microservice.models.logs.event.Event.metadataFromGrpc')
  def testKhaleesiSaveNewEmpty(
      self,
      metadata: MagicMock,
      parent  : MagicMock,
      string  : MagicMock,
  ) -> None :
    """Test reading from gRPC."""
    # Prepare data.
    string.return_value = 'parsed-string'
    instance               = Event()
    instance._state.adding = True  # pylint: disable=protected-access
    grpc = GrpcEventRequest()
    # Execute test.
    instance.khaleesiSave(grpc = grpc)
    # Assert result.
    metadata.assert_called_once()
    parent.assert_called_once()

  @patch('microservice.models.logs.event.Event.metadataToGrpc')
  def testToGrpc(self, metadata: MagicMock) -> None :
    """Test returning a gRPC object."""
    for actionLabel, actionType in GrpcEvent.Action.ActionType.items():
      for resultLabel, resultType in GrpcEvent.Action.ResultType.items():
        for ownerLabel, ownerType in User.UserType.items():
          with self.subTest(action = actionLabel, result = resultLabel, owner = ownerLabel):
            # Prepare data.
            metadata.reset_mock()
            instance = Event(
              targetType       = 'target-type',
              targetId         = 'target-id',
              targetOwnerId    = 'owner-id',
              targetOwnerType  = ownerLabel,
              actionCrudType   = actionLabel,
              actionCustomType = 'action-type',
              actionResult     = resultLabel,
              actionDetails    = 'action-details',
            )
            # Execute test.
            result = instance.toGrpc()
            # Assert result.
            metadata.assert_called_once()
            self.assertEqual(instance.targetType      , result.event.target.type)
            self.assertEqual(instance.targetId        , result.event.target.id)
            self.assertEqual(instance.targetOwnerId   , result.event.target.owner.id)
            self.assertEqual(ownerType                , result.event.target.owner.type)
            self.assertEqual(actionType               , result.event.action.crudType)
            self.assertEqual(instance.actionCustomType, result.event.action.customType)
            self.assertEqual(resultType               , result.event.action.result)
            self.assertEqual(instance.actionDetails   , result.event.action.details)

  @patch('microservice.models.logs.event.Event.metadataToGrpc')
  def testToGrpcEmpty(self, metadata: MagicMock) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    event = Event()
    # Execute test.
    event.toGrpc()
    # Assert result.
    metadata.assert_called_once()

  def _createGrpcEvent(
      self, *,
      owner : 'User.UserType.V',
      action: 'GrpcEvent.Action.ActionType.V',
      result: 'GrpcEvent.Action.ResultType.V'
  ) -> GrpcEventRequest :
    """Utility method for creating gRPC Events."""
    grpc = GrpcEventRequest()

    grpc.event.target.type       = 'target-type'
    grpc.event.target.id         = 'target-id'
    grpc.event.target.owner.type = owner
    grpc.event.target.owner.id   = 'owner-id'

    grpc.event.action.crudType   = action
    grpc.event.action.customType = 'custom-action'
    grpc.event.action.result     = result
    grpc.event.action.details    = 'details'

    return grpc
