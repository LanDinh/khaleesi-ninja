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


@patch('microservice.models.event.AUDIT_EVENT')
@patch('microservice.models.event.parse_uuid')
@patch.object(Event.objects.model, 'log_metadata')
class EventManagerTestCase(TransactionTestCase):
  """Test the event logs objects manager."""

  def test_log_event(self, metadata: MagicMock, uuid: MagicMock, audit_metric: MagicMock) -> None :
    """Test logging a gRPC event."""
    for action_label, action_type in GrpcEvent.Action.ActionType.items():
      for result_label, result_type in GrpcEvent.Action.ResultType.items():
        with self.subTest(action = action_label, result = result_label):
          # Prepare data.
          metadata.reset_mock()
          metadata.return_value = {}
          uuid.return_value = (uuid4(), '')
          now = datetime.now(tz = timezone.utc)
          grpc_event = GrpcEvent()
          grpc_event.request_metadata.caller.request_id       = 'metadata-request-id'
          grpc_event.request_metadata.caller.khaleesi_gate    = 'metadata-khaleesi-gate'
          grpc_event.request_metadata.caller.khaleesi_service = 'metadata-khaleesi-service'
          grpc_event.request_metadata.caller.grpc_service     = 'metadata-grpc-service'
          grpc_event.request_metadata.caller.grpc_method      = 'metadata-grpc-method'
          grpc_event.request_metadata.user.id   = 'origin-system'
          grpc_event.request_metadata.user.type = User.UserType.SYSTEM
          grpc_event.request_metadata.timestamp.FromDatetime(now)
          grpc_event.target.type     = 'target-type'
          grpc_event.target.id       = 13
          grpc_event.target.owner.id = str(uuid4())
          grpc_event.action.crud_type   = action_type
          grpc_event.action.custom_type = 'action-type'
          grpc_event.action.result      = result_type
          grpc_event.action.details     = 'action-description'
          # Execute test.
          result = Event.objects.log_event(grpc_event = grpc_event)
          # Assert result.
          audit_metric.inc.assert_not_called()
          metadata.assert_called_once()
          self.assertEqual(grpc_event.request_metadata, metadata.call_args.kwargs['metadata'])
          self.assertEqual(''                         , metadata.call_args.kwargs['errors'])
          self.assertEqual(grpc_event.target.type               , result.target_type)
          self.assertEqual(grpc_event.target.id                 , result.target_id)
          self.assertEqual(grpc_event.action.crud_type          , result.action_crud_type)
          self.assertEqual(grpc_event.action.custom_type        , result.action_custom_type)
          self.assertEqual(grpc_event.action.result             , result.action_result)
          self.assertEqual(grpc_event.action.details            , result.action_details)

  def test_log_event_empty(
      self,
      metadata: MagicMock,
      uuid: MagicMock,
      audit_metric: MagicMock,
  ) -> None :
    """Test logging an empty gRPC event."""
    # Prepare data.
    uuid.return_value = (uuid4(), '')
    metadata.return_value = {}
    grpc_event = GrpcEvent()
    # Execute test.
    result = Event.objects.log_event(grpc_event = grpc_event)
    # Assert result.
    audit_metric.inc.assert_not_called()
    metadata.assert_called_once()
    self.assertEqual('', metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)

  def test_log_event_appends_uuid_errors(
      self,
      metadata: MagicMock,
      uuid: MagicMock,
      audit_metric: MagicMock,
  ) -> None :
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
    audit_metric.inc.assert_not_called()
    metadata.assert_called_once()
    result_errors =  metadata.call_args.kwargs['errors']
    for _, error in errors:
      self.assertEqual(1, result_errors.count(error))

  def test_log_event_audit_event_for_server_start(
      self,
      metadata: MagicMock,
      uuid: MagicMock,
      audit_metric: MagicMock,
  ) -> None :
    """Test that server starts log audit events."""
    for action in [
        GrpcEvent.Action.ActionType.START,
        GrpcEvent.Action.ActionType.END,
    ]:
      with self.subTest(action = GrpcEvent.Action.ActionType.Name(action)):
        # Prepare data.
        audit_metric.reset_mock()
        uuid.return_value = (uuid4(), '')
        metadata.return_value = {}
        grpc_event = GrpcEvent()
        grpc_event.action.crud_type = action
        grpc_event.target.type = 'core.core.server'
        # Execute test.
        Event.objects.log_event(grpc_event = grpc_event)
        # Assert result.
        audit_metric.inc.assert_called_once_with(event = grpc_event)


class EventTestCase(SimpleTestCase):
  """Test the event logs models."""

  def test_to_grpc_event(self) -> None :
    """Test that general mapping to gRPC works."""
    for action_label, action_type in GrpcEvent.Action.ActionType.items():
      for result_label, result_type in GrpcEvent.Action.ResultType.items():
        for user_label, user_type in User.UserType.items():
          with self.subTest(action = action_label, result = result_label, user = user_label):
            # Prepare data.
            event = Event(
              meta_caller_request_id       = 'request-id',
              meta_caller_khaleesi_gate    = 'khaleesi-gate',
              meta_caller_khaleesi_service = 'khaleesi-service',
              meta_caller_grpc_service     = 'grpc-service',
              meta_caller_grpc_method      = 'grpc-method',
              meta_user_id                 = 'origin-user',
              meta_user_type               = user_type,
              meta_event_timestamp         = datetime.now(tz = timezone.utc),
              meta_logged_timestamp        = datetime.now(tz = timezone.utc),
              target_type  = 'target-type',
              target_id    = 13,
              target_owner = uuid4(),
              action_crud_type   = action_type,
              action_custom_type = 'action-type',
              action_result      = result_type,
              action_details     = 'action_details',
            )
            # Execute test.
            result = event.to_grpc_event()
            # Assert result.
            self.assertEqual(
              event.meta_caller_request_id,
              result.request_metadata.caller.request_id,
            )
            self.assertEqual(
              event.meta_caller_khaleesi_gate,
              result.request_metadata.caller.khaleesi_gate,
            )
            self.assertEqual(
              event.meta_caller_khaleesi_service,
              result.request_metadata.caller.khaleesi_service,
            )
            self.assertEqual(
              event.meta_caller_grpc_service,
              result.request_metadata.caller.grpc_service,
            )
            self.assertEqual(
              event.meta_caller_grpc_method,
              result.request_metadata.caller.grpc_method,
            )
            self.assertEqual(
              event.meta_event_timestamp,
              result.request_metadata.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
            )
            self.assertEqual(
              event.meta_logged_timestamp,
              result.request_metadata.logged_timestamp.ToDatetime().replace(tzinfo = timezone.utc),
            )
            self.assertEqual(event.meta_user_id  , result.request_metadata.user.id)
            self.assertEqual(event.meta_user_type, result.request_metadata.user.type)
            self.assertEqual(event.target_type      , result.target.type)
            self.assertEqual(event.target_id        , result.target.id)
            self.assertEqual(str(event.target_owner), result.target.owner.id)
            self.assertEqual(event.action_crud_type  , result.action.crud_type)
            self.assertEqual(event.action_custom_type, result.action.custom_type)
            self.assertEqual(event.action_result     , result.action.result)
            self.assertEqual(event.action_details    , result.action.details)

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
