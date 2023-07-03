"""Metric utility."""

# Python.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, cast
from uuid import uuid4

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.grpc.channels import CHANNEL_MANAGER
from khaleesi.core.grpc.requestMetadata import addGrpcServerSystemRequestMetadata
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.metrics.requests import INCOMING_REQUESTS, OUTGOING_REQUESTS, RequestsMetric
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.proto.core_pb2 import User, RequestMetadata, GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import Event, ServiceCallData, EmptyRequest
from khaleesi.proto.core_sawmill_pb2_grpc import ForesterStub


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


@dataclass
class GrpcData:
  """Data representing gRPC calls."""
  khaleesiGate   : str
  khaleesiService: str
  grpcService    : str
  grpcMethod     : str


@dataclass
class EventData:
  """Data for initializing event metrics."""
  caller: GrpcData
  targetType: str
  userTypes: List['User.UserType.V'] = field(
    default_factory = lambda: [ v for l, v in User.UserType.items() ],
  )
  actionCrudTypes: List['Event.Action.ActionType.V'] = field(
    default_factory = lambda: [ v for l, v in Event.Action.ActionType.items() ],
  )
  actionCustomTypes: List[str] = field(default_factory = list)
  resultTypes: List['Event.Action.ResultType.V'] = field(
    default_factory = lambda: [ v for l, v in Event.Action.ResultType.items() ],
  )


class BaseMetricInitializer(ABC):
  """Collect info for initializing metrics."""

  ownName      : str
  httpRequestId: str
  grpcRequestId: str

  # noinspection PyUnusedLocal
  def __init__(self, *, httpRequestId: str) -> None :
    self.ownName = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME']
    self.httpRequestId = httpRequestId
    self.grpcRequestId = str(uuid4())

  @abstractmethod
  def initializeMetrics(self) -> None :
    """Initialize the metrics."""

  def initializeMetricsWithData(self, *, events: List[EventData]) -> None :
    """Initialize the provided metrics."""
    self._initializeRequests()
    self._initializeEvents(events = events)

  @abstractmethod
  def getServiceCallData(self, *, request: EmptyRequest) -> ServiceCallData :
    """Fetch service registry data."""

  def requests(self) -> ServiceCallData :
    """Fetch the data for request metrics."""
    request = EmptyRequest()
    addGrpcServerSystemRequestMetadata(
      metadata      = request.requestMetadata,
      httpRequestId = self.httpRequestId,
      grpcRequestId = self.grpcRequestId,
      grpcMethod    = 'INITIALIZE_REQUEST_METRICS',
    )
    return self.getServiceCallData(request = request)

  def _initializeRequests(self) -> None :
    """Initialize the request metrics to 0."""
    requests = self.requests()
    for request in requests.callList:
      requestMetadata = RequestMetadata()
      self._buildRequestMetadata(requestMetadata = requestMetadata, caller = request.call)
      if requestMetadata.caller.grpcService == self.ownName:
        userList = [ (User.UserType.Name(User.UserType.SYSTEM), User.UserType.SYSTEM) ]
      else:
        userList = User.UserType.items()
      for _, user in userList:
        requestMetadata.user.type = user
        for rawPeer in request.calls:
          self._registerRequest(
            requestMetadata = requestMetadata,
            rawPeer         = rawPeer,
            metric          = OUTGOING_REQUESTS,
          )
        for rawPeer in request.calledBy:
          self._registerRequest(
            requestMetadata = requestMetadata,
            rawPeer         = rawPeer,
            metric          = INCOMING_REQUESTS,
          )

  def _registerRequest(
      self, *,
      requestMetadata: RequestMetadata,
      rawPeer        : GrpcCallerDetails,
      metric         : RequestsMetric,
  ) -> None :
    """Register the request to the specified metric."""
    peer = RequestMetadata()
    self._buildRequestMetadata(requestMetadata = peer, caller = rawPeer)
    if peer.caller.grpcService == self.ownName and \
        requestMetadata.user.type != User.UserType.SYSTEM:
      return  # pragma: no cover
    for status in StatusCode:
      metric.register(status = status, request = requestMetadata, peer = peer)


  def _buildRequestMetadata(
      self, *,
      requestMetadata: RequestMetadata,
      caller: GrpcCallerDetails,
  ) -> None :
    """Build the request metadata to register metrics."""
    requestMetadata.caller.khaleesiGate    = caller.khaleesiGate
    requestMetadata.caller.khaleesiService = caller.khaleesiService
    requestMetadata.caller.grpcService     = caller.grpcService
    requestMetadata.caller.grpcMethod      = caller.grpcMethod

  def _initializeEvents(self, *, events: List[EventData]) -> None :
    """Initialize the event metrics to 0."""
    for eventData in events:
      for userType in eventData.userTypes:
        for resultType in eventData.resultTypes:
          for actionCrudType in eventData.actionCrudTypes:
            self._buildEvent(
              eventData      = eventData,
              userType       = userType,
              resultType     = resultType,
              actionCrudType = actionCrudType,
            )
          for actionCustomType in eventData.actionCustomTypes:
            self._buildEvent(
              eventData        = eventData,
              userType         = userType,
              resultType       = resultType,
              actionCustomType = actionCustomType,
            )

  def _buildEvent(
      self, *,
      eventData       : EventData,
      userType        : 'User.UserType.V',
      resultType      : 'Event.Action.ResultType.V',
      actionCrudType  : Optional['Event.Action.ActionType.V'] = None,
      actionCustomType: Optional[str] = None,
  ) -> None :
    """Build the event object to register metrics."""
    if actionCrudType and actionCustomType:
      raise ProgrammingException(  # pragma: no cover
        privateMessage = 'Only one of actionCrudType and actionCustomType are allowed',
        privateDetails = '',
      )
    event = Event()
    event.requestMetadata.user.type              = userType
    event.requestMetadata.caller.khaleesiGate    = eventData.caller.khaleesiGate
    event.requestMetadata.caller.khaleesiService = eventData.caller.khaleesiService
    event.requestMetadata.caller.grpcService     = eventData.caller.grpcService
    event.requestMetadata.caller.grpcMethod      = eventData.caller.grpcMethod
    event.target.type                            = eventData.targetType
    event.action.result                          = resultType

    if actionCrudType:
      event.action.crudType = actionCrudType
    if actionCustomType:
      event.action.customType = actionCustomType

    AUDIT_EVENT.register(event = event)


# noinspection PyAbstractClass
class MetricInitializer(BaseMetricInitializer):
  """MetricInitializer which gets service registry data via gRPC."""

  stub    : ForesterStub

  def __init__(self, *, httpRequestId: str) -> None :
    super().__init__(httpRequestId = httpRequestId)
    channel = CHANNEL_MANAGER.getChannel(gate = 'core', service = 'sawmill')
    self.stub = ForesterStub(channel)  # type: ignore[no-untyped-call]

  def getServiceCallData(self, *, request: EmptyRequest) -> ServiceCallData :
    """Fetch the data for request metrics."""
    return cast(ServiceCallData, self.stub.GetServiceCallData(request))
