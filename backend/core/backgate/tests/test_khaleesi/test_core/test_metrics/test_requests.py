"""Test the requests metrics."""

# Python.
from functools import partial
from itertools import product
from typing import Callable
from unittest.mock import patch, MagicMock

# gGRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.metrics.requests import OUTGOING_REQUESTS, INCOMING_REQUESTS
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from tests.test_khaleesi.test_core.test_metrics.test_util import CounterMetricTestMixin


class RequestsMetricTestMixin(CounterMetricTestMixin):
  """Test mixin for requests metrics."""

  subTest: Callable  # type: ignore[type-arg]

  def test_inc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    for status, (user_label, user_type) in product(StatusCode, User.UserType.items()):
      with self.subTest(status = status.name, user = user_label):
        # Prepare data.
        request_metadata = self._get_request_metadata(user = user_type)
        # Execute test & assert result.
        self.execute_and_assert_counter(
          method = partial(
            self.metric.inc,
            status  = status,
            request = request_metadata,
            peer    = request_metadata,
          ),
          status  = status,
          request = request_metadata,
          peer    = request_metadata,
        )

  @patch('khaleesi.core.metrics.requests.CounterMetric.get_value')
  def test_get_value(self, super_get_value: MagicMock) -> None :
    """Test string replacement for empty strings."""
    callee_grpc_service = 'callee-service'
    callee_grpc_method  = 'callee-method'
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
        with self.subTest(user = user_label, status = status, test = label):
          # Prepare data.
          super_get_value.reset_mock()
          request = self._get_request_metadata(user = user_type, **request_attributes)  # type: ignore[arg-type]  # pylint: disable=line-too-long
          peer    = self._get_request_metadata(user = user_type, **request_attributes)  # type: ignore[arg-type]  # pylint: disable=line-too-long
          peer.caller.grpc_service = callee_grpc_service
          peer.caller.grpc_method  = callee_grpc_method
          # Execute test.
          self.metric.get_value(
            status  = status,
            request = request,
            peer    = peer,
          )
          # Assert result.
          super_get_value.assert_called_once_with(
            status                = status,
            user                  = user_type,
            grpc_service          = request.caller.grpc_service     or 'UNKNOWN',
            grpc_method           = request.caller.grpc_method      or 'UNKNOWN',
            peer_khaleesi_gate    = peer.caller.khaleesi_gate       or 'UNKNOWN',
            peer_khaleesi_service = peer.caller.khaleesi_service    or 'UNKNOWN',
            peer_grpc_service     = peer.caller.grpc_service        or 'UNKNOWN',
            peer_grpc_method      = peer.caller.grpc_method         or 'UNKNOWN',
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


class OutgoingRequestsMetricTestCase(RequestsMetricTestMixin, SimpleTestCase):
  """Test the outgoing requests metric."""

  metric = OUTGOING_REQUESTS


class IncomingRequestsMetricTestCase(RequestsMetricTestMixin, SimpleTestCase):
  """Test the outgoing requests metric."""

  metric = INCOMING_REQUESTS
