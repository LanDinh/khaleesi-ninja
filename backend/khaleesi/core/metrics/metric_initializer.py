"""Metric utility."""

# Python.
from dataclasses import dataclass, field
from typing import List, Optional

# khaleesi.ninja.
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event


@dataclass
class GrpcData:
  """Data representing gRPC calls."""
  khaleesi_gate: str
  khaleesi_service: str
  grpc_service: str
  grpc_method: str


@dataclass
class EventData:
  """Data for initializing event metrics."""
  caller: GrpcData
  target_type: str
  user_types: List['User.UserType.V'] = field(
    default_factory = lambda: [ v for l, v in User.UserType.items() ],
  )
  action_crud_types: List['Event.Action.ActionType.V'] = field(
    default_factory = lambda: [ v for l, v in Event.Action.ActionType.items() ],
  )
  action_custom_types: List[str] = field(default_factory = list)
  result_types: List['Event.Action.ResultType.V'] = field(
    default_factory = lambda: [ v for l, v in Event.Action.ResultType.items() ],
  )


class BaseMetricInitializer:
  """Collect info for initializing metrics."""

  def initialize_metrics(self) -> None :
    """Initialize the metrics."""
    raise ProgrammingException(private_details = 'Need to override initialize_metrics!')

  def initialize_metrics_with_data(self, *, events: List[EventData]) -> None :
    """Initialize the provided metrics."""
    self._initialize_events(events = events)

  def _initialize_events(self, *, events: List[EventData]) -> None :
    for event_data in events:
      for user_type in event_data.user_types:
        for result_type in event_data.result_types:
          for action_crud_type in event_data.action_crud_types:
            self._build_event(
              event_data       = event_data,
              user_type        = user_type,
              result_type      = result_type,
              action_crud_type = action_crud_type,
            )
          for action_custom_type in event_data.action_custom_types:
            self._build_event(
              event_data         = event_data,
              user_type          = user_type,
              result_type        = result_type,
              action_custom_type = action_custom_type,
            )

  def _build_event(
      self, *,
      event_data        : EventData,
      user_type         : 'User.UserType.V',
      result_type       : 'Event.Action.ResultType.V',
      action_crud_type  : Optional['Event.Action.ActionType.V'] = None,
      action_custom_type: Optional[str] = None,
  ) -> None :
    if action_crud_type and action_custom_type:
      raise ProgrammingException(  # pragma: no cover
        private_details = 'Only one of action_crud_type and action_custom_type are allowed',
      )
    event = Event()
    event.request_metadata.user.type               = user_type
    event.request_metadata.caller.khaleesi_gate    = event_data.caller.khaleesi_gate
    event.request_metadata.caller.khaleesi_service = event_data.caller.khaleesi_service
    event.request_metadata.caller.grpc_service     = event_data.caller.grpc_service
    event.request_metadata.caller.grpc_method      = event_data.caller.grpc_method
    event.target.type                              = event_data.target_type
    event.action.result                            = result_type

    if action_crud_type:
      event.action.crud_type = action_crud_type
    if action_custom_type:
      event.action.custom_type = action_custom_type

    AUDIT_EVENT.register(event = event)
