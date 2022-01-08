"""Test the event logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from uuid import uuid4

# khaleesi.ninja.
from khaleesi.core.test_util import TransactionTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent
from microservice.models import Event


@patch('microservice.models.event.parse_uuid')
@patch.object(Event.objects.model, 'log_metadata')
class EventManagerTestCase(TransactionTestCase):
  """Test the event logs."""

  def test_log_event(self, metadata: MagicMock, uuid: MagicMock) -> None :
    """Test logging a gRPC event."""
    # Prepare data.
    metadata.return_value = {}
    uuid.return_value = (uuid4(), '')
    now = datetime.now(tz = timezone.utc)
    grpc_event = GrpcEvent()
    grpc_event.request_metadata.user.id         = 'origin-system'
    grpc_event.request_metadata.user.type       = User.UserType.SYSTEM
    grpc_event.metadata.timestamp.FromDatetime(now)
    grpc_event.metadata.logger.request_id       = 'metadata-request-id'
    grpc_event.metadata.logger.khaleesi_gate    = 'metadata-khaleesi-gate'
    grpc_event.metadata.logger.khaleesi_service = 'metadata-khaleesi-service'
    grpc_event.metadata.logger.grpc_service     = 'metadata-grpc-service'
    grpc_event.metadata.logger.grpc_method      = 'metadata-grpc-method'
    grpc_event.target.type                      = 'target-type'
    grpc_event.target.id                        = 13
    grpc_event.target.owner.id                  = str(uuid4())
    grpc_event.action.crud_type                 = GrpcEvent.Action.ActionType.CUSTOM
    grpc_event.action.custom_type               = 'action-type'
    grpc_event.action.result                    = GrpcEvent.Action.ResultType.SUCCESS
    grpc_event.action.details                   = 'action-description'
    # Execute test.
    result = Event.objects.log_event(grpc_event = grpc_event)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual(grpc_event.request_metadata.user.id  , result.origin_user)
    self.assertEqual(grpc_event.request_metadata.user.type, result.origin_type)
    self.assertEqual('', metadata.call_args.kwargs['errors'])
    self.assertEqual(grpc_event.target.type               , result.target_type)
    self.assertEqual(grpc_event.target.id                 , result.target_id)
    self.assertEqual(grpc_event.action.custom_type        , result.action_type)
    self.assertEqual(grpc_event.action.result             , result.action_result)
    self.assertEqual(grpc_event.action.details            , result.action_details)

  def test_log_event_empty(self, metadata: MagicMock, uuid: MagicMock) -> None :
    """Test logging an empty gRPC event."""
    # Prepare data.
    uuid.return_value = (uuid4(), '')
    metadata.return_value = {}
    grpc_event = GrpcEvent()
    # Execute test.
    result = Event.objects.log_event(grpc_event = grpc_event)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual('', metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)

  def test_log_event_appends_uuid_errors(self, metadata: MagicMock, uuid: MagicMock) -> None :
    """Test uuid errors get appended correctly."""
    # Prepare data.
    errors = [ (uuid4(), 'invalid target_owner') ]
    uuid.side_effect = errors
    metadata.return_value = {}
    grpc_event = GrpcEvent()
    # Execute test.
    Event.objects.log_event(grpc_event = grpc_event)
    # Assert result.
    self.assertEqual(len(errors), uuid.call_count)
    metadata.assert_called_once()
    result_errors =  metadata.call_args.kwargs['errors']
    for _, error in errors:
      self.assertEqual(1, result_errors.count(error))

  def test_log_event_crud_action_type(self, metadata: MagicMock, uuid: MagicMock) -> None :
    """Test crud action type propagation."""
    # Prepare data.
    uuid.return_value = (uuid4(), '')
    metadata.return_value = {}
    for action_type in [
        action_type for action_type in GrpcEvent.Action.ActionType.DESCRIPTOR.values_by_number  # pylint: disable=protobuf-undefined-attribute
        if action_type != GrpcEvent.Action.ActionType.CUSTOM
    ]:
      grpc_event = GrpcEvent()
      grpc_event.action.crud_type = action_type
      # Execute test.
      result = Event.objects.log_event(grpc_event = grpc_event)
      # Assert result.
      self.assertEqual(action_type, GrpcEvent.Action.ActionType.Value(result.action_type))
      self.assertEqual(''         , result.meta_logging_errors)

  def test_log_event_custom_action_type(self, metadata: MagicMock, uuid: MagicMock) -> None :
    """Test custom action type propagation."""
    # Prepare data.
    uuid.return_value = (uuid4(), '')
    metadata.return_value = {}
    grpc_event = GrpcEvent()
    grpc_event.action.crud_type = GrpcEvent.Action.CUSTOM
    grpc_event.action.custom_type = 'custom type'
    # Execute test.
    result = Event.objects.log_event(grpc_event = grpc_event)
    # Assert result.
    self.assertEqual(grpc_event.action.custom_type, result.action_type)
    self.assertEqual('', result.meta_logging_errors)
