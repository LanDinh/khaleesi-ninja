"""Interceptor test utility."""

# Python.
from typing import Optional, Any, Tuple, Dict, Callable, List
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.grpc import GrpcTestMixin
from khaleesi.proto.core_pb2 import User, RequestMetadata  # pylint: disable=unused-import


class InterceptorTestMixin(GrpcTestMixin):
  """Interceptor test utility."""

  emptyInput = {
      'khaleesiGate'   : '',
      'khaleesiService': '',
      'grpcService'    : '',
      'grpcMethod'     : '',
  }
  metadataRequestParams: List[Tuple[str, Dict[str, Any]]] = [
      ( 'full input'           , {} ),
      ( 'empty khaleesiGate'   , { 'khaleesiGate'   : '' } ),
      ( 'empty khaleesiService', { 'khaleesiService': '' } ),
      ( 'empty grpcService'    , { 'grpcService'    : '' } ),
      ( 'empty grpcMethod'     , { 'grpcMethod'     : '' } ),
      ( 'empty input'          , emptyInput ),
  ]

  def getRequest(
      self, *,
      request        : Optional[Any],
      user           : 'User.UserType.V',
      **requestParams: Any,
  ) -> Tuple[RequestMetadata, Any]:
    """get requestMetadata and final request."""
    if request is None:
      requestMetadata = self.setRequestMetadata(user = user, **requestParams)
      finalRequest    = MagicMock(requestMetadata = requestMetadata)
    else:
      requestMetadata = RequestMetadata()
      finalRequest    = request
    return requestMetadata, finalRequest

  def getInterceptParams(
      self, *,
      method: Callable[[], Any] = lambda *args : None,
  ) -> Dict[str, Any] :
    """Get parameters to pass into the interceptor."""
    return {
        'method': method,
    }

class ServerInterceptorTestMixin(InterceptorTestMixin):
  """Server interceptor test utility."""

  def getInterceptParams(
      self, *,
      context   : MagicMock = MagicMock(),
      method    : Callable[[], Any] = lambda *args : None,
      methodName: str               = '/khaleesi.gate.service.serviceName/methodName',
  ) -> Dict[str, Any] :
    """Get parameters to pass into the server interceptor."""
    return {
        'context'   : context,
        'methodName': methodName,
        **super().getInterceptParams(method = method),
    }

class ClientInterceptorTestMixin(InterceptorTestMixin):
  """Server interceptor test utility."""

  khaleesiGate    = 'Gate'
  khaleesiService = 'Service'
  grpcService     = 'service'
  grpcMethod      = 'method'

  def getInterceptParams(
      self, *,
      method: Callable[[], Any] = lambda *args : None,
  ) -> Dict[str, Any] :
    """Get parameters to pass into the server interceptor."""
    return {
        'callDetails'    : MagicMock(),
        'khaleesiGate'   : self.khaleesiGate,
        'khaleesiService': self.khaleesiService,
        'grpcService'    : self.grpcService,
        'grpcMethod'     : self.grpcMethod,
        **super().getInterceptParams(method = method),
    }
