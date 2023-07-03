"""Metric utility."""

# Python.
from typing import List

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.metrics.metricInitializer import BaseMetricInitializer, EventData, GrpcData
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.proto.core_pb2 import User, GrpcCallerDetails, EmptyRequest
from khaleesi.proto.core_sawmill_pb2 import Event, ServiceCallData
from microservice.models.serviceRegistry import SERVICE_REGISTRY


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class MetricInitializer(BaseMetricInitializer):
  """Collect info for initializing metrics."""

  def __init__(self, *, httpRequestId: str) -> None :
    super().__init__(httpRequestId = httpRequestId)
    # No gRPC call is executed for the gRPC lifecycle methods, so we need to manually add them.
    callerDetails = GrpcCallerDetails()
    callerDetails.khaleesiGate    = khaleesiSettings['METADATA']['GATE']
    callerDetails.khaleesiService = khaleesiSettings['METADATA']['SERVICE']
    callerDetails.grpcService     = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME']
    callerDetails.grpcMethod = \
        khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['LIFECYCLE']['METHOD']
    SERVICE_REGISTRY.addService(callerDetails = callerDetails)

  def initializeMetrics(self) -> None :
    """Initialize the metrics."""
    events = [*self._serverStateEvents()]
    super().initializeMetricsWithData(events = events)

  def getServiceCallData(self, *, request: EmptyRequest) -> ServiceCallData :
    """Fetch the data for request metrics."""
    return SERVICE_REGISTRY.getCallData(owner = request.requestMetadata.grpcCaller)

  def _serverStateEvents(self) -> List[EventData] :
    events = []
    serviceRegistry = SERVICE_REGISTRY.getServiceRegistry()
    for gateName, gate in serviceRegistry.items():
      for serviceName, _ in gate.services.items():
        sharedData = {
            'caller': GrpcData(
              khaleesiGate    = gateName,
              khaleesiService = serviceName,
              grpcService     = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['SERVICE_NAME'],
              grpcMethod = khaleesiSettings['GRPC']['SERVER_METHOD_NAMES']['LIFECYCLE']['METHOD'],
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
