"""Test the requests metrics."""

# Python.
from functools import partial
from itertools import product

# gGRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.requests import (OUTGOING_REQUESTS, INCOMING_REQUESTS)
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from tests.test_khaleesi.test_core.test_metrics.test_util import CounterMetricTestMixin


class RequestsMetricTestMixin(CounterMetricTestMixin):
  """Test mixin for requests metrics."""

  labels = {
      'grpc_service'         : 'grpc-service',
      'grpc_method'          : 'grpc-method',
      'peer_khaleesi_gate'   : 'peer-khaleesi-gate',
      'peer_khaleesi_service': 'peer-khaleesi-service',
      'peer_grpc_service'    : 'peer-grpc-service',
      'peer_grpc_method'     : 'peer-grpc-method',
  }

  def test_inc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    for status, (_, user) in product(StatusCode, User.UserType.items()):
      with self.subTest(status = status.name, user = user):  # type: ignore[attr-defined]  # pylint: disable=no-member
        # Execute test and assert result.
        self.execute_and_assert_counter(
          method = partial(self.metric.inc, status = status, user = user, **self.labels),
          status = status,
          user   = user,
          **self.labels
        )


class OutgoingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = OUTGOING_REQUESTS


class IncomingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = INCOMING_REQUESTS
