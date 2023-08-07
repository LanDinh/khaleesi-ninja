"""Metric utility."""

# Python.
from typing import List

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.metrics.metricInitializer import BaseMetricInitializer, EventData, GrpcData
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.proto.core_pb2 import User, GrpcCallerDetails, EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import Event, AppCallData
from microservice.models.siteRegistry import SITE_REGISTRY


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class MetricInitializer(BaseMetricInitializer):
  """Collect info for initializing metrics."""

  def __init__(self, *, httpRequestId: str) -> None :
    super().__init__(httpRequestId = httpRequestId)
    # No gRPC call is executed for the gRPC lifecycle methods, so we need to manually add them.
    callerDetails = GrpcCallerDetails()
    callerDetails.site    = khaleesiSettings['METADATA']['SITE']
    callerDetails.app     = khaleesiSettings['METADATA']['APP']
    callerDetails.service = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME']
    callerDetails.method  = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['LIFECYCLE']['METHOD']
    SITE_REGISTRY.addApp(callerDetails = callerDetails)

  def initializeMetrics(self) -> None :
    """Initialize the metrics."""
    events = [*self._serverStateEvents()]
    super().initializeMetricsWithData(events = events)

  def getAppCallData(self, *, request: EmptyRequest) -> AppCallData :
    """Fetch the data for request metrics."""
    return SITE_REGISTRY.getCallData(owner = request.requestMetadata.grpcCaller)

  def _serverStateEvents(self) -> List[EventData] :
    events = []
    siteRegistry = SITE_REGISTRY.getSiteRegistry()
    for siteName, site in siteRegistry.items():
      for appName, _ in site.apps.items():
        sharedData = {
            'caller': GrpcData(
              site    = siteName,
              app     = appName,
              service = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME'],
              method  = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['LIFECYCLE']['METHOD'],
            ),
            'targetType' : khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['LIFECYCLE']['TARGET'],
            'userTypes'  :  [ User.UserType.SYSTEM ],
        }
        events.append(EventData(
          **sharedData,  # type: ignore[arg-type]
          actionCrudTypes = [ Event.Action.ActionType.START ],
          resultTypes     = [ Event.Action.ResultType.SUCCESS, Event.Action.ResultType.FATAL ],
        ))
        events.append(EventData(
          **sharedData,  # type: ignore[arg-type]
          actionCrudTypes = [ Event.Action.ActionType.END ],
          resultTypes     = [
              Event.Action.ResultType.SUCCESS,
              Event.Action.ResultType.ERROR,
              Event.Action.ResultType.FATAL,
          ],
        ))
    return events
