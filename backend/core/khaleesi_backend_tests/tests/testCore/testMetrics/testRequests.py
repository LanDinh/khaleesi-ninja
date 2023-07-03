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
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from tests.testCore.testMetrics.testUtil import CounterMetricTestMixin


class RequestsMetricTestMixin(CounterMetricTestMixin):
  """Test mixin for requests metrics."""

  subTest: Callable  # type: ignore[type-arg]

  def testInc(self) -> None :
    """Test incrementing the counter."""
    # Prepare data.
    for status, (userLabel, userType) in product(StatusCode, User.UserType.items()):
      with self.subTest(status = status.name, user = userLabel):
        # Prepare data.
        requestMetadata = self._getRequestMetadata(user = userType)
        # Execute test & assert result.
        self.executeAndAssertCounter(
          method = partial(
            self.metric.inc,
            status  = status,
            request = requestMetadata,
            peer    = requestMetadata,
          ),
          status  = status,
          request = requestMetadata,
          peer    = requestMetadata,
        )

  @patch('khaleesi.core.metrics.requests.CounterMetric.getValue')
  def testGetValue(self, superGetValue: MagicMock) -> None :
    """Test string replacement for empty strings."""
    calleeGrpcService = 'callee-service'
    calleeGrpcMethod  = 'callee-method'
    for status, (userLabel, userType) in product(StatusCode, User.UserType.items()):
      for label, requestAttributes in [
          ( 'full input'        , {} ),
          ( 'empty input'       , {
              'khaleesiGate'   : '',
              'khaleesiService': '',
              'grpcService'    : '',
              'grpcMethod'     : '',
          } ),
          ( 'empty gate'        , {'khaleesiGate'   : ''} ),
          ( 'empty service'     , {'khaleesiService': ''} ),
          ( 'empty grpc service', {'grpcService'    : ''} ),
          ( 'empty grpc method' , {'grpcMethod'     : ''} ),
      ]:
        with self.subTest(user = userLabel, status = status, test = label):
          # Prepare data.
          superGetValue.reset_mock()
          request = self._getRequestMetadata(user = userType, **requestAttributes)  # type: ignore[arg-type]  # pylint: disable=line-too-long
          peer    = self._getRequestMetadata(user = userType, **requestAttributes)  # type: ignore[arg-type]  # pylint: disable=line-too-long
          peer.grpcCaller.grpcService = calleeGrpcService
          peer.grpcCaller.grpcMethod  = calleeGrpcMethod
          # Execute test.
          self.metric.getValue(
            status  = status,
            request = request,
            peer    = peer,
          )
          # Assert result.
          superGetValue.assert_called_once_with(
            status              = status,
            user                = userType,
            grpcService         = request.grpcCaller.grpcService  or 'UNKNOWN',
            grpcMethod          = request.grpcCaller.grpcMethod   or 'UNKNOWN',
            peerKhaleesiGate    = peer.grpcCaller.khaleesiGate    or 'UNKNOWN',
            peerKhaleesiService = peer.grpcCaller.khaleesiService or 'UNKNOWN',
            peerGrpcService     = peer.grpcCaller.grpcService     or 'UNKNOWN',
            peerGrpcMethod      = peer.grpcCaller.grpcMethod      or 'UNKNOWN',
          )


  def _getRequestMetadata(
      self, *,
      user           : 'User.UserType.V',
      khaleesiGate   : str = 'khaleesi-gate',
      khaleesiService: str = 'khaleesi-service',
      grpcService    : str = 'grpc-service',
      grpcMethod     : str = 'grpc-method',
  ) -> RequestMetadata :
    """Get the request metadata."""
    requestMetadata = RequestMetadata()
    requestMetadata.grpcCaller.khaleesiGate    = khaleesiGate
    requestMetadata.grpcCaller.khaleesiService = khaleesiService
    requestMetadata.grpcCaller.grpcService     = grpcService
    requestMetadata.grpcCaller.grpcMethod      = grpcMethod
    requestMetadata.user.type                  = user
    return requestMetadata


class OutgoingRequestsMetricTestCase(RequestsMetricTestMixin, SimpleTestCase):
  """Test the outgoing requests metric."""

  metric = OUTGOING_REQUESTS


class IncomingRequestsMetricTestCase(RequestsMetricTestMixin, SimpleTestCase):
  """Test the outgoing requests metric."""

  metric = INCOMING_REQUESTS
