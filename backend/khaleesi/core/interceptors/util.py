"""Interceptor utility."""

# Python.
from typing import Tuple

# khaleesi.ninja.
from khaleesi.core.shared.logger import LOGGER


class Interceptor:
  """Interceptor utility."""

  skip_list = [
      '/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo',
      '/grpc.health.v1.Health/Check',
      '/grpc.health.v1.Health/Watch',
  ]

  def skip_interceptors(self, *, raw: str) -> bool :
    """Skip interceptors for utility provided by libraries."""
    if raw in self.skip_list:
      LOGGER.debug(f'Skip logging of {raw}')
      return True
    return False

  def process_method_name(self, *, raw: str) -> Tuple[str, str, str, str] :
    """Process the method name and return (service, method)."""
    parts = raw.split('/')
    service          = parts[1].split('.') if len(parts) > 1 else ''.split('.')
    khaleesi_gate    = service[1] if len(service) > 1 else ''
    khaleesi_service = service[2] if len(service) > 2 else ''
    grpc_service     = service[3] if len(service) > 3 else ''
    grpc_method      = parts[2]   if len(parts) > 2   else ''
    return (
        self.string_or_unknown(value = khaleesi_gate),
        self.string_or_unknown(value = khaleesi_service),
        self.string_or_unknown(value = grpc_service),
        self.string_or_unknown(value = grpc_method),
    )

  def string_or_unknown(self, *, value: str) -> str :
    """Either return the value, or UNKNOWN if empty."""
    if value:
      return value
    return 'UNKNOWN'
