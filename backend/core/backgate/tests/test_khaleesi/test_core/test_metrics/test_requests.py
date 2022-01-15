"""Test the requests metrics."""

# Python.
from functools import partial
from itertools import product
from unittest.mock import patch, MagicMock

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

  @patch('khaleesi.core.metrics.requests.CounterMetric.get_value')
  def test_get_value(self, super_get_value: MagicMock) -> None :
    """Test string replacement for empty strings."""
    callee_grpc_service = 'callee-service'
    callee_grpc_method = 'callee-method'
    for status, (user_label, user_type) in product(StatusCode, User.UserType.items()):
      for label, request_attributes in [
          ( 'full input'        , {} ),
          ( 'empty input'       , {
              'khaleesi_gate'   : '',
              'khaleesi_service': '',
              'grpc_service'    : '',
              'grpc_method'     : '',
          } ),
          ( 'empty gate'        , {'khaleesi_gate'   : ''} ),
          ( 'empty service'     , {'khaleesi_service': ''} ),
          ( 'empty grpc service', {'grpc_service'    : ''} ),
          ( 'empty grpc method' , {'grpc_method'     : ''} ),
      ]:
        with self.subTest(user = user_label, status = status, test = label):  # type: ignore[attr-defined]  # pylint: disable=no-member,line-too-long
          # Prepare data.
          super_get_value.reset_mock()
          request_metadata = self._get_request_metadata(user = user_type, **request_attributes)  # type: ignore[arg-type]  # pylint: disable=line-too-long
          # Execute test.
          self.metric.get_value(
            request_metadata = request_metadata,
            status           = status,
            grpc_service     = callee_grpc_service,
            grpc_method      = callee_grpc_method,
          )
          # Assert result.
          super_get_value.assert_called_once_with(
            status                = status,
            grpc_service          = callee_grpc_service,
            grpc_method           = callee_grpc_method,
            user                  = user_type,
            peer_khaleesi_gate    = request_metadata.caller.khaleesi_gate    or 'UNKNOWN',
            peer_khaleesi_service = request_metadata.caller.khaleesi_service or 'UNKNOWN',
            peer_grpc_service     = request_metadata.caller.grpc_service     or 'UNKNOWN',
            peer_grpc_method      = request_metadata.caller.grpc_method      or 'UNKNOWN',
          )


  @staticmethod
  def _get_request_metadata(
      *,
      user            : 'User.UserType.V',
      khaleesi_gate   : str = 'khaleesi-gate',
      khaleesi_service: str = 'khaleesi-service',
      grpc_service    : str = 'grpc-service',
      grpc_method     : str = 'grpc-method',
  ) -> RequestMetadata :
    """Get the request metadata."""
    request_metadata = RequestMetadata()
    request_metadata.caller.khaleesi_gate    = khaleesi_gate
    request_metadata.caller.khaleesi_service = khaleesi_service
    request_metadata.caller.grpc_service     = grpc_service
    request_metadata.caller.grpc_method      = grpc_method
    request_metadata.user.type               = user
    return request_metadata


class OutgoingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = OUTGOING_REQUESTS


class IncomingRequestsMetricTestCase(SimpleTestCase, RequestsMetricTestMixin):
  """Test the outgoing requests metric."""

  metric = INCOMING_REQUESTS
