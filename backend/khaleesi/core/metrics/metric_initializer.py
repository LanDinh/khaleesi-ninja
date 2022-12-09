"""Metric utility."""

# Python.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, cast

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.grpc.channels import ChannelManager
from khaleesi.core.grpc.request_metadata import add_grpc_server_system_request_metadata
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.metrics.requests import INCOMING_REQUESTS, OUTGOING_REQUESTS, RequestsMetric
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.proto.core_pb2 import User, RequestMetadata, GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import Event, ServiceCallData, EmptyRequest
from khaleesi.proto.core_sawmill_pb2_grpc import ForesterStub


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


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


class BaseMetricInitializer(ABC):
  """Collect info for initializing metrics."""

  own_name: str

  # noinspection PyUnusedLocal
  def __init__(self, *, channel_manager: ChannelManager) -> None :  # pylint: disable=unused-argument
    self.own_name = khaleesi_settings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME']

  @abstractmethod
  def initialize_metrics(self) -> None :
    """Initialize the metrics."""

  def initialize_metrics_with_data(self, *, events: List[EventData]) -> None :
    """Initialize the provided metrics."""
    self._initialize_requests()
    self._initialize_events(events = events)

  @abstractmethod
  def get_service_call_data(self, *, request: EmptyRequest) -> ServiceCallData :
    """Fetch service registry data."""

  def requests(self) -> ServiceCallData :
    """Fetch the data for request metrics."""
    request = EmptyRequest()
    add_grpc_server_system_request_metadata(
      request      = request,
      grpc_method  = 'INITIALIZE_REQUEST_METRICS',
    )
    return self.get_service_call_data(request = request)

  def _initialize_requests(self) -> None :
    """Initialize the request metrics to 0."""
    requests = self.requests()
    for request in requests.call_list:
      request_metadata = RequestMetadata()
      self._build_request_metadata(request_metadata = request_metadata, caller = request.call)
      if request_metadata.caller.grpc_service == self.own_name:
        user_list = [ (User.UserType.Name(User.UserType.SYSTEM), User.UserType.SYSTEM) ]
      else:
        user_list = User.UserType.items()
      for _, user in user_list:
        request_metadata.user.type = user
        for raw_peer in request.calls:
          self._register_request(
            request_metadata = request_metadata,
            raw_peer = raw_peer,
            metric = OUTGOING_REQUESTS,
          )
        for raw_peer in request.called_by:
          self._register_request(
            request_metadata = request_metadata,
            raw_peer = raw_peer,
            metric = INCOMING_REQUESTS,
          )

  def _register_request(
      self, *,
      request_metadata: RequestMetadata,
      raw_peer: GrpcCallerDetails,
      metric: RequestsMetric,
  ) -> None :
    """Register the request to the specified metric."""
    peer = RequestMetadata()
    self._build_request_metadata(request_metadata = peer, caller = raw_peer)
    if peer.caller.grpc_service == self.own_name and \
        request_metadata.user.type != User.UserType.SYSTEM:
      return
    for status in StatusCode:
      metric.register(status = status, request = request_metadata, peer = peer)


  def _build_request_metadata(
      self, *,
      request_metadata: RequestMetadata,
      caller: GrpcCallerDetails,
  ) -> None :
    """Build the request metadata to register metrics."""
    request_metadata.caller.khaleesi_gate    = caller.khaleesi_gate
    request_metadata.caller.khaleesi_service = caller.khaleesi_service
    request_metadata.caller.grpc_service     = caller.grpc_service
    request_metadata.caller.grpc_method      = caller.grpc_method

  def _initialize_events(self, *, events: List[EventData]) -> None :
    """Initialize the event metrics to 0."""
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
    """Build the event object to register metrics."""
    if action_crud_type and action_custom_type:
      raise ProgrammingException(  # pragma: no cover
        private_message = 'Only one of action_crud_type and action_custom_type are allowed',
        private_details = '',
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


# noinspection PyAbstractClass
class MetricInitializer(BaseMetricInitializer):
  """MetricInitializer which gets service registry data via gRPC."""

  stub    : ForesterStub

  def __init__(self, *, channel_manager: ChannelManager) -> None :
    super().__init__(channel_manager = channel_manager)
    channel = channel_manager.get_channel(gate = 'core', service = 'sawmill')
    self.stub = ForesterStub(channel)  # type: ignore[no-untyped-call]

  def get_service_call_data(self, *, request: EmptyRequest) -> ServiceCallData :
    """Fetch the data for request metrics."""
    return cast(ServiceCallData, self.stub.GetServiceCallData(request))
