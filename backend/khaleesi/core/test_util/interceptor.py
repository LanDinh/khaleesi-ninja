"""Interceptor test utility."""

# Python.
from typing import Optional, Any, Tuple, Dict, Callable
from unittest.mock import MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.grpc import GrpcTestMixin
from khaleesi.proto.core_pb2 import User, RequestMetadata  # pylint: disable=unused-import


class InterceptorTestMixin(GrpcTestMixin):
  """Interceptor test utility."""

  empty_input = {
      'khaleesi_gate'   : '',
      'khaleesi_service': '',
      'grpc_service'    : '',
      'grpc_method'     : '',
  }
  metadata_request_params = [
      ( 'full input'            , {} ),
      ( 'empty khaleesi_gate'   , { 'khaleesi_gate'   : '' } ),
      ( 'empty khaleesi_service', { 'khaleesi_service': '' } ),
      ( 'empty grpc_service'    , { 'grpc_service'    : '' } ),
      ( 'empty grpc_method'     , { 'grpc_method'     : '' } ),
      ( 'empty input'           , empty_input ),
  ]

  def get_request(
      self, *,
      request: Optional[Any],
      user: 'User.UserType.V',
      **request_params: Any,
  ) -> Tuple[RequestMetadata, Any]:
    """get request_metadata and final request."""
    if request is None:
      request_metadata = self.set_request_metadata(user = user, **request_params)
      final_request = MagicMock(request_metadata = request_metadata)
    else:
      request_metadata = RequestMetadata()
      final_request = request
    return request_metadata, final_request

  def get_intercept_params(
      self, *,
      method: Callable[[], Any] = lambda *args : None,
  ) -> Dict[str, Any] :
    """Get parameters to pass into the interceptor."""
    return {
        'method' : method,
    }

class ServerInterceptorTestMixin(InterceptorTestMixin):
  """Server interceptor test utility."""

  service_name = 'service-name'
  method_name  = 'method-name'

  def get_intercept_params(
      self, *,
      method: Callable[[], Any] = lambda *args : None,
  ) -> Dict[str, Any] :
    """Get parameters to pass into the server interceptor."""
    return {
        'context'     : MagicMock(),
        'service_name': self.service_name,
        'method_name' : self.method_name,
        **super().get_intercept_params(method = method),
    }

class ClientInterceptorTestMixin(InterceptorTestMixin):
  """Server interceptor test utility."""

  khaleesi_gate    = 'Gate'
  khaleesi_service = 'Service'
  grpc_service     = 'service'
  grpc_method      = 'method'

  def get_intercept_params(
      self, *,
      method: Callable[[], Any] = lambda *args : None,
  ) -> Dict[str, Any] :
    """Get parameters to pass into the server interceptor."""
    return {
        'call_details'     : MagicMock(),
        'khaleesi_gate'    : self.khaleesi_gate,
        'khaleesi_service' : self.khaleesi_service,
        'grpc_service'     : self.grpc_service,
        'grpc_method'      : self.grpc_method,
        **super().get_intercept_params(method = method),
    }
