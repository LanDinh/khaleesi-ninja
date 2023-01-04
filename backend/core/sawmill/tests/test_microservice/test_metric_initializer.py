"""Test the metric initializer."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Event
from microservice.metric_initializer import MetricInitializer
from microservice.models.service_registry import (
  KhaleesiGate,
  KhaleesiService,
  GrpcService,
  GrpcMethod,
)


@patch('microservice.metric_initializer.BaseMetricInitializer.initialize_metrics_with_data')
@patch('microservice.metric_initializer.SERVICE_REGISTRY')
class MetricInitializerTestCase(SimpleTestCase):
  """Test the metric initializer."""

  def test_init(self, service_registry: MagicMock, *_: MagicMock) -> None :
    """Test initialization."""
    # Prepare data & execute test.
    MetricInitializer(backgate_request_id = 'backgate-request')
    # Assert result.
    service_registry.add_service.assert_called_once()

  def test_requests(self, service_registry: MagicMock, *_: MagicMock) -> None :
    """Test the requests are fetched correctly."""
    # Prepare data.
    metric_initializer = MetricInitializer(backgate_request_id = 'backgate-request')
    # Execute test.
    metric_initializer.requests()
    # Assert result.
    service_registry.get_call_data.assert_called_once()

  def test_initialize_metrics(
      self,
      service_registry: MagicMock,
      parent: MagicMock,
  ) -> None :
    """Test initialization of metrics."""
    # Prepare data.
    metric_initializer = MetricInitializer(backgate_request_id = 'backgate-request')
    khaleesi_gate_name    = 'khaleesi-gate'
    khaleesi_service_name = 'khaleesi-service'
    grpc_service_name     = 'grpc-server'
    grpc_method_name      = 'lifecycle'
    service_registry.get_service_registry.return_value = {
        khaleesi_gate_name: KhaleesiGate(
          services = {
              khaleesi_service_name: KhaleesiService(
                services = {
                    grpc_service_name: GrpcService(
                      methods = { grpc_method_name: GrpcMethod() }
                    )
                }
              )
          }
        )
    }
    # Execute test.
    metric_initializer.initialize_metrics()
    # Assert result.
    parent.assert_called_once()
    arguments = parent.call_args
    start = False
    end = False
    for event in arguments.kwargs['events']:
      self.assertEqual(khaleesi_gate_name   , event.caller.khaleesi_gate)
      self.assertEqual(khaleesi_service_name, event.caller.khaleesi_service)
      self.assertEqual(grpc_service_name    , event.caller.grpc_service)
      self.assertEqual(grpc_method_name     , event.caller.grpc_method)
      self.assertEqual('core.core.server'   , event.target_type)
      self.assertEqual(1                    , len(event.user_types))
      self.assertEqual(User.UserType.SYSTEM , event.user_types[0])
      self.assertEqual(1                    , len(event.action_crud_types))
      if event.action_crud_types[0] == Event.Action.ActionType.START:
        start = True
      if event.action_crud_types[0] == Event.Action.ActionType.END:
        end = True
    self.assertTrue(start)
    self.assertTrue(end)
