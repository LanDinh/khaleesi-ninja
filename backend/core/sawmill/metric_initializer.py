"""Metric utility."""

# Python.
from typing import List

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.metrics.metric_initializer import BaseMetricInitializer, EventData, GrpcData
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.proto.core_pb2 import User, GrpcCallerDetails
from khaleesi.proto.core_sawmill_pb2 import Event
from microservice.models.service_registry import SERVICE_REGISTRY


khaleesi_settings: KhaleesiNinjaSettings  = settings.KHALEESI_NINJA


class MetricInitializer(BaseMetricInitializer):
  """Collect info for initializing metrics."""

  def __init__(self) -> None :
    caller_details = GrpcCallerDetails()
    caller_details.khaleesi_gate    = khaleesi_settings['METADATA']['GATE']
    caller_details.khaleesi_service = khaleesi_settings['METADATA']['SERVICE']
    caller_details.grpc_service     = khaleesi_settings['CONSTANTS']['GRPC_SERVER']['NAME']
    caller_details.grpc_method      = khaleesi_settings['CONSTANTS']['GRPC_SERVER']['LIFECYCLE']
    SERVICE_REGISTRY.add_service(caller_details = caller_details)

  def initialize_metrics(self) -> None :
    """Initialize the metrics."""
    events = [
        *self._server_state_events(),
    ]
    super().initialize_metrics_with_data(events = events)

  def _server_state_events(self) -> List[EventData] :
    events = []
    service_registry = SERVICE_REGISTRY.get_service_registry()
    for gate_name, gate in service_registry.items():
      for service_name, _ in gate.services.items():
        shared_data = {
            'caller': GrpcData(
              khaleesi_gate    = gate_name,
              khaleesi_service = service_name,
              grpc_service     = khaleesi_settings['CONSTANTS']['GRPC_SERVER']['NAME'],
              grpc_method      = khaleesi_settings['CONSTANTS']['GRPC_SERVER']['LIFECYCLE'],
            ),
            'target_type' : 'core.core.server',
            'user_types'  :  [ User.UserType.SYSTEM ],
        }
        events.append(EventData(
          **shared_data,  # type: ignore[arg-type]
          action_crud_types = [ Event.Action.ActionType.START ],
          result_types      = [ Event.Action.ResultType.SUCCESS, Event.Action.ResultType.FATAL ],
        ))
        events.append(EventData(
          **shared_data,  # type: ignore[arg-type]
          action_crud_types = [ Event.Action.ActionType.END ],
          result_types      = [
              Event.Action.ResultType.SUCCESS,
              Event.Action.ResultType.ERROR,
              Event.Action.ResultType.FATAL,
          ],
        ))
    return events
