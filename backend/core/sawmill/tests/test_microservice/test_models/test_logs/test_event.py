"""Test the event logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.core.test_util.test_case import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event as GrpcEvent
from microservice.models import Event
from microservice.test_util import ModelRequestMetadataMixin


@patch('microservice.models.logs.event.AUDIT_EVENT')
@patch('microservice.models.logs.event.parse_string')
@patch.object(Event.objects.model, 'log_metadata')
class EventManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the event logs objects manager."""

  def test_log_event(
      self,
      metadata: MagicMock,
      string: MagicMock,
      audit_metric: MagicMock,
  ) -> None :
    """Test logging a gRPC event."""
    for action_label, action_type in GrpcEvent.Action.ActionType.items():
      for result_label, result_type in GrpcEvent.Action.ResultType.items():
        for user_label, user_type in User.UserType.items():
          for owner_label, owner_type in User.UserType.items():
            for log_event_metric in [True, False]:
              with self.subTest(
                  action           = action_label,
                  result           = result_label,
                  user             = user_label,
                  log_event_metric = log_event_metric,
                  owner            = owner_label,
              ):
                # Prepare data.
                audit_metric.reset_mock()
                metadata.reset_mock()
                metadata.return_value = {}
                string.return_value = 'parsed-string'
                now = datetime.now(tz = timezone.utc)
                grpc_event = GrpcEvent()
                self.set_request_metadata(
                  request_metadata = grpc_event.request_metadata,
                  now              = now,
                  user             = user_type,
                )
                grpc_event.target.type        = 'target-type'
                grpc_event.target.id          = 'target-id'
                grpc_event.target.owner.id    = 'target-owner'
                grpc_event.target.owner.type  = owner_type
                grpc_event.action.crud_type   = action_type
                grpc_event.action.custom_type = 'action-type'
                grpc_event.action.result      = result_type
                grpc_event.action.details     = 'action-description'
                grpc_event.logger_send_metric = log_event_metric
                # Execute test.
                result = Event.objects.log_event(grpc_event = grpc_event)
                # Assert result.
                metadata.assert_called_once()
                self.assertEqual(grpc_event.request_metadata, metadata.call_args.kwargs['metadata'])
                self.assertEqual([]                           , metadata.call_args.kwargs['errors'])
                self.assertEqual(owner_label                  , result.target_owner_type)
                self.assertEqual(action_label                 , result.action_crud_type)
                self.assertEqual(grpc_event.action.custom_type, result.action_custom_type)
                self.assertEqual(result_label                 , result.action_result)
                if log_event_metric:
                  audit_metric.inc.assert_called_once()
                else:
                  audit_metric.inc.assert_not_called()

  def test_log_event_empty(
      self,
      metadata: MagicMock,
      string: MagicMock,
      audit_metric: MagicMock,
  ) -> None :
    """Test logging an empty gRPC event."""
    # Prepare data.
    string.return_value = 'parsed-string'
    metadata.return_value = {}
    grpc_event = GrpcEvent()
    # Execute test.
    result = Event.objects.log_event(grpc_event = grpc_event)
    # Assert result.
    audit_metric.inc.assert_not_called()
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.meta_logging_errors)


class EventTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the event logs models."""

  def test_to_grpc_event(self) -> None :
    """Test that general mapping to gRPC works."""
    for action_label, action_type in GrpcEvent.Action.ActionType.items():
      for result_label, result_type in GrpcEvent.Action.ResultType.items():
        for user_label, user_type in User.UserType.items():
          for owner_label, owner_type in User.UserType.items():
            with self.subTest(
                action = action_label,
                result = result_label,
                user   = user_label,
                owner  = owner_label,
            ):
              # Prepare data.
              event = Event(
                target_type        = 'target-type',
                target_id          = 'target-id',
                target_owner_id    = 'owner-id',
                target_owner_type  = owner_label,
                action_crud_type   = action_label,
                action_custom_type = 'action-type',
                action_result      = result_label,
                action_details     = 'action_details',
                **self.model_full_request_metadata(user = user_type),
              )
              # Execute test.
              result = event.to_grpc_event_response()
              # Assert result.
              self.assert_grpc_request_metadata(
                model = event,
                grpc = result.event.request_metadata,
                grpc_response = result.event_metadata,
              )
              self.assertEqual(event.target_type       , result.event.target.type)
              self.assertEqual(owner_type              , result.event.target.owner.type)
              self.assertEqual(action_type             , result.event.action.crud_type)
              self.assertEqual(event.action_custom_type, result.event.action.custom_type)
              self.assertEqual(result_type             , result.event.action.result)
              self.assertEqual(event.action_details    , result.event.action.details)

  def test_empty_to_grpc_event(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    event = Event(**self.model_empty_request_metadata())
    # Execute test.
    result = event.to_grpc_event_response()
    # Assert result.
    self.assertIsNotNone(result)
