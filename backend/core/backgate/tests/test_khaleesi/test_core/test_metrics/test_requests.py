"""Test the requests metrics."""

# Python.
from functools import partial
from itertools import product

# gGRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.requests import OUTGOING_REQUESTS, INCOMING_REQUESTS
from khaleesi.core.test_util import SimpleTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from tests.test_khaleesi.test_core.test_metrics.test_util import CounterMetricTestMixin


class RequestsMetricTestMixin(CounterMetricTestMixin):
  """Test mixin for requests metrics."""

  labels = {
      'grpc_service'         : 'grpc-service',
      'grpc_method'          : 'grpc-method',
  }

  def test_inc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    for status, (user_label, user_type) in product(StatusCode, User.UserType.items()):
      with self.subTest(status = status.name, user = user_label):  # type: ignore[attr-defined]  # pylint: disable=no-member
        # Prepare data.
        request_metadata = self._get_request_metadata(user = user_type)
        # Execute test and assert result.
        self.execute_and_assert_counter(
          method = partial(
            self.metric.inc,
            status = status,
            request_metadata = request_metadata,
            **self.labels,
          ),
          status = status,
          request_metadata = request_metadata,
          **self.labels
        )

  @staticmethod
  def _get_request_metadata(*, user: 'User.UserType.V') -> RequestMetadata :
    """Get the request metadata."""
    request_metadata = RequestMetadata()
    request_metadata.caller.khaleesi_gate    = 'khaleesi-gate'
    request_metadata.caller.khaleesi_service = 'khaleesi-service'
    request_metadata.caller.grpc_service     = 'grpc-service'
    request_metadata.caller.grpc_method      = 'grpc-method'
    request_metadata.user.type               = user
    return request_metadata


class OutgoingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = OUTGOING_REQUESTS


class IncomingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = INCOMING_REQUESTS
