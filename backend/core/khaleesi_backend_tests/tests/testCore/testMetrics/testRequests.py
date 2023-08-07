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
    calleeService = 'callee-service'
    calleeMethod  = 'callee-method'
    for status, (userLabel, userType) in product(StatusCode, User.UserType.items()):
      for label, requestAttributes in [
          ( 'full input'   , {} ),
          ( 'empty input'  , { 'site': '', 'app': '', 'service': '', 'method': '' } ),
          ( 'empty site'   , {'site'   : ''} ),
          ( 'empty app'    , {'app'    : ''} ),
          ( 'empty service', {'service': ''} ),
          ( 'empty method' , {'method' : ''} ),
      ]:
        with self.subTest(user = userLabel, status = status, test = label):
          # Prepare data.
          superGetValue.reset_mock()
          request = self._getRequestMetadata(user = userType, **requestAttributes)  # type: ignore[arg-type]  # pylint: disable=line-too-long
          peer    = self._getRequestMetadata(user = userType, **requestAttributes)  # type: ignore[arg-type]  # pylint: disable=line-too-long
          peer.grpcCaller.service = calleeService
          peer.grpcCaller.method  = calleeMethod
          # Execute test.
          self.metric.getValue(
            status  = status,
            request = request,
            peer    = peer,
          )
          # Assert result.
          superGetValue.assert_called_once_with(
            status      = status,
            user        = userType,
            service     = request.grpcCaller.service or 'UNKNOWN',
            method      = request.grpcCaller.method  or 'UNKNOWN',
            peerSite    = peer.grpcCaller.site       or 'UNKNOWN',
            peerApp     = peer.grpcCaller.app        or 'UNKNOWN',
            peerService = peer.grpcCaller.service    or 'UNKNOWN',
            peerMethod  = peer.grpcCaller.method     or 'UNKNOWN',
          )


  def _getRequestMetadata(
      self, *,
      user   : 'User.UserType.V',
      site   : str = 'site',
      app    : str = 'app',
      service: str = 'service',
      method : str = 'method',
  ) -> RequestMetadata :
    """Get the request metadata."""
    requestMetadata = RequestMetadata()
    requestMetadata.grpcCaller.site    = site
    requestMetadata.grpcCaller.app     = app
    requestMetadata.grpcCaller.service = service
    requestMetadata.grpcCaller.method  = method
    requestMetadata.user.type          = user
    return requestMetadata


class OutgoingRequestsMetricTestCase(RequestsMetricTestMixin, SimpleTestCase):
  """Test the outgoing requests metric."""

  metric = OUTGOING_REQUESTS


class IncomingRequestsMetricTestCase(RequestsMetricTestMixin, SimpleTestCase):
  """Test the outgoing requests metric."""

  metric = INCOMING_REQUESTS
