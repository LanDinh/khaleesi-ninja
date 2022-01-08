"""Test the event logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from uuid import uuid4

# khaleesi.ninja.
from khaleesi.core.test_util import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent
from microservice.models import Event


@patch('microservice.models.event.parse_uuid')
@patch.object(Event.objects.model, 'log_metadata')
class EventManagerTestCase(TransactionTestCase):
  """Test the event logs objects manager."""

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
    uuid.return_value = (uuid4(), '')
    metadata.return_value = {}
    for action_type in [
        action_type for action_type in GrpcEvent.Action.ActionType.DESCRIPTOR.values_by_number  # pylint: disable=protobuf-undefined-attribute
        if action_type != GrpcEvent.Action.ActionType.CUSTOM
    ]:
      with self.subTest(action_type = GrpcEvent.Action.ActionType.Name(action_type)):
        # Prepare data.
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


class EventTestCase(SimpleTestCase):
  """Test the event logs models."""

  def test_to_grpc_event(self) -> None :
    """Test that general mapping to gRPC works."""
    # Prepare data.
    event = Event(
      meta_event_timestamp         = datetime.now(tz = timezone.utc),
      meta_logged_timestamp        = datetime.now(tz = timezone.utc),
      meta_logger_request_id       = 'request-id',
      meta_logger_khaleesi_gate    = 'khaleesi-gate',
      meta_logger_khaleesi_service = 'khaleesi-service',
      meta_logger_grpc_service     = 'grpc-service',
      meta_logger_grpc_method      = 'grpc-method',
      target_type                  = 'target-type',
      target_id                    = 13,
      target_owner                 = uuid4(),
      origin_user                  = 'origin-user',
      origin_type                  = 1,
      action_type                  = 'action-type',
      action_result                = 2,
      action_details               = 'action_details',
    )
    # Execute test.
    result = event.to_grpc_event()
    # Assert result.
    self.assertEqual(event.meta_event_timestamp,
      result.metadata.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(
      event.meta_logged_timestamp,
      result.metadata.logged_timestamp.ToDatetime().replace(tzinfo = timezone.utc),
    )
    self.assertEqual(event.meta_logger_request_id      , result.metadata.logger.request_id)
    self.assertEqual(event.meta_logger_khaleesi_gate   , result.metadata.logger.khaleesi_gate)
    self.assertEqual(event.meta_logger_khaleesi_service, result.metadata.logger.khaleesi_service)
    self.assertEqual(event.meta_logger_grpc_service    , result.metadata.logger.grpc_service)
    self.assertEqual(event.meta_logger_grpc_method     , result.metadata.logger.grpc_method)
    self.assertEqual(event.target_type                 , result.target.type)
    self.assertEqual(event.target_id                   , result.target.id)
    self.assertEqual(str(event.target_owner)           , result.target.owner.id)
    self.assertEqual(event.origin_user                 , result.request_metadata.user.id)
    self.assertEqual(event.origin_type                 , result.request_metadata.user.type)
    self.assertEqual(GrpcEvent.Action.ActionType.CUSTOM, result.action.crud_type)
    self.assertEqual(event.action_type                 , result.action.custom_type)
    self.assertEqual(event.action_result               , result.action.result)
    self.assertEqual(event.action_details              , result.action.details)

  def test_empty_to_grpc_event(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    event = Event(
      meta_event_timestamp  = datetime.now(tz = timezone.utc),
      meta_logged_timestamp = datetime.now(tz = timezone.utc),
    )
    # Execute test.
    result = event.to_grpc_event()
    # Assert result.
    self.assertIsNotNone(result)

  def test_to_grpc_event_with_target_owner(self) -> None :
    """Test that mapping to gRPC works with target owners."""
    # Prepare data.
    event = Event(
      meta_event_timestamp  = datetime.now(tz = timezone.utc),
      meta_logged_timestamp = datetime.now(tz = timezone.utc),
      target_owner = 'target-owner',
    )
    # Execute test.
    result = event.to_grpc_event()
    # Assert result.
    self.assertEqual(event.target_owner, result.target.owner.id)

  def test_to_grpc_event_without_target_owner(self) -> None :
    """Test that mapping to gRPC works without target owners."""
    # Prepare data.
    event = Event(
      meta_event_timestamp  = datetime.now(tz = timezone.utc),
      meta_logged_timestamp = datetime.now(tz = timezone.utc),
    )
    # Execute test.
    result = event.to_grpc_event()
    # Assert result.
    self.assertEqual('', result.target.owner.id)

  def test_to_grpc_event_with_action_crud_type(self) -> None :
    """Test that mapping to gRPC works for actions with crud types."""
    for action_type in [
        action_type for action_type in GrpcEvent.Action.ActionType.DESCRIPTOR.values_by_number  # pylint: disable=protobuf-undefined-attribute
        if action_type != GrpcEvent.Action.ActionType.CUSTOM
    ]:
      action_name = GrpcEvent.Action.ActionType.Name(action_type)
      with self.subTest(action_type = action_name):
        # Prepare data.
        event = Event(
          meta_event_timestamp  = datetime.now(tz = timezone.utc),
          meta_logged_timestamp = datetime.now(tz = timezone.utc),
          action_type = action_name
        )
        # Execute test.
        result = event.to_grpc_event()
        # Assert result.
        self.assertEqual(action_type, result.action.crud_type)
        self.assertEqual(''         , result.action.custom_type)

  def test_to_grpc_event_with_action_custom_type(self) -> None :
    """Test that mapping to gRPC works for actions with custom types."""
    # Prepare data.
    event = Event(
      meta_event_timestamp  = datetime.now(tz = timezone.utc),
      meta_logged_timestamp = datetime.now(tz = timezone.utc),
      action_type = 'custom-action'
    )
    # Execute test.
    result = event.to_grpc_event()
    # Assert result.
    self.assertEqual(GrpcEvent.Action.ActionType.CUSTOM, result.action.crud_type)
    self.assertEqual(event.action_type                 , result.action.custom_type)
