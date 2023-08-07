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
      'site'   : '',
      'app'    : '',
      'service': '',
      'method' : '',
  }
  metadataRequestParams: List[Tuple[str, Dict[str, Any]]] = [
      ( 'full input'   , {} ),
      ( 'empty site'   , { 'site'   : '' } ),
      ( 'empty app'    , { 'app': '' } ),
      ( 'empty service', { 'service'    : '' } ),
      ( 'empty method' , { 'method'     : '' } ),
      ( 'empty input'  , emptyInput ),
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
      executableMethod: Callable[[], Any] = lambda *args : None,
  ) -> Dict[str, Any] :
    """Get parameters to pass into the interceptor."""
    return {
        'executableMethod': executableMethod,
    }

class ServerInterceptorTestMixin(InterceptorTestMixin):
  """Server interceptor test utility."""

  def getInterceptParams(
      self, *,
      context         : MagicMock = MagicMock(),
      executableMethod: Callable[[], Any] = lambda *args : None,
      rawMethod       : str               = '/khaleesi.site.service.serviceName/methodName',
  ) -> Dict[str, Any] :
    """Get parameters to pass into the server interceptor."""
    return {
        'context'  : context,
        'rawMethod': rawMethod,
        **super().getInterceptParams(executableMethod = executableMethod),
    }

class ClientInterceptorTestMixin(InterceptorTestMixin):
  """Server interceptor test utility."""

  site    = 'site'
  app     = 'app'
  service = 'service'
  method  = 'method'

  def getInterceptParams(
      self, *,
      executableMethod: Callable[[], Any] = lambda *args : None,
  ) -> Dict[str, Any] :
    """Get parameters to pass into the server interceptor."""
    return {
        'callDetails': MagicMock(),
        'site'       : self.site,
        'app'        : self.app,
        'service'    : self.service,
        'method'     : self.method,
        **super().getInterceptParams(executableMethod = executableMethod),
    }
