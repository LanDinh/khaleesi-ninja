"""Test the event logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.grpc import GrpcTestMixin
from khaleesi.core.testUtil.testCase import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent
from microservice.models import Event
from microservice.testUtil import ModelRequestMetadataMixin


@patch('microservice.models.logs.event.AUDIT_EVENT')
@patch('microservice.models.logs.event.parseString')
@patch.object(Event.objects.model, 'logMetadata')
class EventManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the event logs objects manager."""

  def testLogEvent(self, metadata: MagicMock, string: MagicMock, auditMetric: MagicMock) -> None :
    """Test logging a gRPC event."""
    for actionLabel, actionType in GrpcEvent.Action.ActionType.items():
      for resultLabel, resultType in GrpcEvent.Action.ResultType.items():
        for userLabel, userType in User.UserType.items():
          for ownerLabel, ownerType in User.UserType.items():
            for logEventMetric in [True, False]:
              with self.subTest(
                  action         = actionLabel,
                  result         = resultLabel,
                  user           = userLabel,
                  logEventMetric = logEventMetric,
                  owner          = ownerLabel,
              ):
                # Prepare data.
                auditMetric.reset_mock()
                metadata.reset_mock()
                metadata.return_value = {}
                string.return_value = 'parsed-string'
                now = datetime.now(tz = timezone.utc)
                grpcEvent = GrpcEvent()
                self.setRequestMetadata(
                  requestMetadata = grpcEvent.requestMetadata,
                  now             = now,
                  user            = userType,
                )
                grpcEvent.id                = 'event-id'
                grpcEvent.target.type       = 'target-type'
                grpcEvent.target.id         = 'target-id'
                grpcEvent.target.owner.id   = 'target-owner'
                grpcEvent.target.owner.type = ownerType
                grpcEvent.action.crudType   = actionType
                grpcEvent.action.customType = 'action-type'
                grpcEvent.action.result     = resultType
                grpcEvent.action.details    = 'action-description'
                grpcEvent.loggerSendMetric  = logEventMetric
                # Execute test.
                result = Event.objects.logEvent(grpcEvent = grpcEvent)
                # Assert result.
                metadata.assert_called_once()
                self.assertEqual(grpcEvent.requestMetadata  , metadata.call_args.kwargs['metadata'])
                self.assertEqual([]                         , metadata.call_args.kwargs['errors'])
                self.assertEqual(ownerLabel                 , result.targetOwnerType)
                self.assertEqual(actionLabel                , result.actionCrudType)
                self.assertEqual(grpcEvent.action.customType, result.actionCustomType)
                self.assertEqual(resultLabel                , result.actionResult)
                self.assertEqual(grpcEvent.action.details   , result.actionDetails)
                if logEventMetric:
                  auditMetric.inc.assert_called_once()
                else:
                  auditMetric.inc.assert_not_called()

  def testLogEventEmpty(
      self,
      metadata   : MagicMock,
      string     : MagicMock,
      auditMetric: MagicMock,
  ) -> None :
    """Test logging an empty gRPC event."""
    # Prepare data.
    string.return_value = 'parsed-string'
    metadata.return_value = {}
    grpcEvent = GrpcEvent()
    # Execute test.
    result = Event.objects.logEvent(grpcEvent = grpcEvent)
    # Assert result.
    auditMetric.inc.assert_not_called()
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.metaLoggingErrors)


class EventTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the event logs models."""

  def testToGrpcEvent(self) -> None :
    """Test that general mapping to gRPC works."""
    for actionLabel, actionType in GrpcEvent.Action.ActionType.items():
      for resultLabel, resultType in GrpcEvent.Action.ResultType.items():
        for userLabel, userType in User.UserType.items():
          for ownerLabel, ownerType in User.UserType.items():
            with self.subTest(
                action = actionLabel,
                result = resultLabel,
                user   = userLabel,
                owner  = ownerLabel,
            ):
              # Prepare data.
              event = Event(
                eventId          = 'event-id',
                targetType       = 'target-type',
                targetId         = 'target-id',
                targetOwnerId    = 'owner-id',
                targetOwnerType  = ownerLabel,
                actionCrudType   = actionLabel,
                actionCustomType = 'action-type',
                actionResult     = resultLabel,
                actionDetails    = 'action-details',
                **self.modelFullRequestMetadata(user = userType),
              )
              # Execute test.
              result = event.toGrpc()
              # Assert result.
              self.assertGrpcRequestMetadata(
                model        = event,
                grpc         = result.event.requestMetadata,
                grpcResponse = result.eventMetadata,
              )
              self.assertEqual(event.eventId         , result.event.id)
              self.assertEqual(event.targetType      , result.event.target.type)
              self.assertEqual(ownerType             , result.event.target.owner.type)
              self.assertEqual(actionType            , result.event.action.crudType)
              self.assertEqual(event.actionCustomType, result.event.action.customType)
              self.assertEqual(resultType            , result.event.action.result)
              self.assertEqual(event.actionDetails   , result.event.action.details)

  def testEmptyToGrpcEvent(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    event = Event(**self.modelEmptyRequestMetadata())
    # Execute test.
    result = event.toGrpc()
    # Assert result.
    self.assertIsNotNone(result)
