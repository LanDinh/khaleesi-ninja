"""Interceptor to handle state of requests."""

# Python.
from uuid import uuid4

# khaleesi.ninja.
from khaleesi.core.interceptors.server.request_state import BaseRequestStateServerInterceptor
from khaleesi.core.shared.state import STATE
from khaleesi.core.logging.structured_logger import StructuredLogger
from khaleesi.proto.core_pb2 import RequestMetadata


class BackgateRequestStateServerInterceptor(BaseRequestStateServerInterceptor):
  """RequestStateServerInterceptor that chooses its own backgate request ID and logs it."""

  structured_logger: StructuredLogger

  def __init__(self, *, structured_logger: StructuredLogger) -> None :
    """Initialize the RequestStateServerInterceptor."""
    super().__init__(structured_logger = structured_logger)
    self.structured_logger = structured_logger

  def set_backgate_request_id(self, *, upstream: RequestMetadata) -> None :
    """Set the backgate request id."""
    STATE.request.backgate_request_id = str(uuid4())
    self.structured_logger.log_backgate_request()
