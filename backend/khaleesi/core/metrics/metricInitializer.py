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
from khaleesi.core.grpc.requestMetadata import addSystemRequestMetadata
from khaleesi.core.metrics.audit import AUDIT_EVENT
from khaleesi.core.metrics.requests import INCOMING_REQUESTS, OUTGOING_REQUESTS, RequestsMetric
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.core.shared.exceptions import ProgrammingException
from khaleesi.proto.core_pb2 import User, RequestMetadata, GrpcCallerDetails, EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import Event, EventRequest, AppCallData
from khaleesi.proto.core_sawmill_pb2_grpc import ForesterStub


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


@dataclass
class GrpcData:
  """Data representing gRPC calls."""
  site   : str
  app    : str
  service: str
  method : str


@dataclass
class EventData:
  """Data for initializing event metrics."""
  caller    : GrpcData
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
  def getAppCallData(self, *, request: EmptyRequest) -> AppCallData :
    """Fetch app registry data."""

  def requests(self) -> AppCallData :
    """Fetch the data for request metrics."""
    request = EmptyRequest()
    addSystemRequestMetadata(
      metadata      = request.requestMetadata,
      httpRequestId = self.httpRequestId,
      grpcRequestId = self.grpcRequestId,
      method = 'INITIALIZE_REQUEST_METRICS',
    )
    return self.getAppCallData(request = request)

  def _initializeRequests(self) -> None :
    """Initialize the request metrics to 0."""
    requests = self.requests()
    for request in requests.callList:
      requestMetadata = RequestMetadata()
      self._buildRequestMetadata(requestMetadata = requestMetadata, caller = request.call)
      if requestMetadata.grpcCaller.service == self.ownName:
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
    if peer.grpcCaller.service == self.ownName and \
        requestMetadata.user.type != User.UserType.SYSTEM:
      return  # pragma: no cover
    for status in StatusCode:
      metric.register(status = status, request = requestMetadata, peer = peer)


  def _buildRequestMetadata(
      self, *,
      requestMetadata: RequestMetadata,
      caller         : GrpcCallerDetails,
  ) -> None :
    """Build the request metadata to register metrics."""
    requestMetadata.grpcCaller.site    = caller.site
    requestMetadata.grpcCaller.app     = caller.app
    requestMetadata.grpcCaller.service = caller.service
    requestMetadata.grpcCaller.method  = caller.method

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
    event = EventRequest()
    event.requestMetadata.user.type          = userType
    event.requestMetadata.grpcCaller.site    = eventData.caller.site
    event.requestMetadata.grpcCaller.app     = eventData.caller.app
    event.requestMetadata.grpcCaller.service = eventData.caller.service
    event.requestMetadata.grpcCaller.method  = eventData.caller.method
    event.event.target.type                  = eventData.targetType
    event.event.action.result                = resultType

    if actionCrudType:
      event.event.action.crudType = actionCrudType
    if actionCustomType:
      event.event.action.customType = actionCustomType

    AUDIT_EVENT.register(event = event)


# noinspection PyAbstractClass
class MetricInitializer(BaseMetricInitializer):
  """MetricInitializer which gets app registry data via gRPC."""

  stub    : ForesterStub

  def __init__(self, *, httpRequestId: str) -> None :
    super().__init__(httpRequestId = httpRequestId)
    channel   = CHANNEL_MANAGER.getChannel(site = 'core', app = 'sawmill')
    self.stub = ForesterStub(channel)  # type: ignore[no-untyped-call]

  def getAppCallData(self, *, request: EmptyRequest) -> AppCallData :
    """Fetch the data for request metrics."""
    return cast(AppCallData, self.stub.GetAppCallData(request))
