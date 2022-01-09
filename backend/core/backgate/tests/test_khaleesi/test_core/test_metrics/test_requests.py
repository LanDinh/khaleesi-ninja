"""Test the requests metrics."""

# Python.
from functools import partial
from itertools import product

# gGRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.requests import (
    OUTGOING_REQUESTS,
    INCOMING_REQUESTS,
    RequestUserMetricType,
)
from khaleesi.core.test_util import SimpleTestCase
from tests.test_khaleesi.test_core.test_metrics.test_util import CounterMetricTestMixin


class RequestsMetricTestMixin(CounterMetricTestMixin):
  """Test mixin for requests metrics."""

  def test_inc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    labels = {
        'grpc_service'         : 'grpc-service',
        'grpc_method'          : 'grpc-method',
        'peer_khaleesi_gate'   : 'peer-khaleesi-gate',
        'peer_khaleesi_service': 'peer-khaleesi-service',
        'peer_grpc_service'    : 'peer-grpc-service',
        'peer_grpc_method'     : 'peer-grpc-method',
    }
    for status, user in product(StatusCode, RequestUserMetricType):
      with self.subTest(status = status.name, user = user.name):  # type: ignore[attr-defined]  # pylint: disable=no-member
        # Execute test and assert result.
        self.execute_and_assert(
          method = partial(self.metric.inc, status = status, user = user, **labels),
          status = status,
          user   = user,
          **labels
        )


class OutgoingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = OUTGOING_REQUESTS


class IncomingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = INCOMING_REQUESTS
