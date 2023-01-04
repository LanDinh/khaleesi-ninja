"""Interceptor to handle state of requests."""

# Python.
from uuid import uuid4

# khaleesi.ninja.
from khaleesi.core.interceptors.server.request_state import BaseRequestStateServerInterceptor
from khaleesi.core.shared.state import STATE
from khaleesi.core.shared.singleton import SINGLETON
from khaleesi.proto.core_pb2 import RequestMetadata


class BackgateRequestStateServerInterceptor(BaseRequestStateServerInterceptor):
  """RequestStateServerInterceptor that chooses its own backgate request ID and logs it."""

  def set_backgate_request_id(self, *, upstream: RequestMetadata) -> None :
    """Set the backgate request id."""
    STATE.request.backgate_request_id = str(uuid4())
    SINGLETON.structured_logger.log_backgate_request()
