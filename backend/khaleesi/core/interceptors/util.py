"""Interceptor utility."""

# Python.
from typing import Tuple


class Interceptor:
  """Interceptor utility."""

  skipList = [
      '/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo',
      '/grpc.health.v1.Health/Check',
      '/grpc.health.v1.Health/Watch',
  ]

  def skipInterceptors(self, *, raw: str) -> bool :
    """Skip interceptors for utility provided by libraries."""
    return raw in self.skipList

  def processMethodName(self, *, raw: str) -> Tuple[str, str, str, str] :
    """Process the method name and return (service, method)."""
    parts = raw.split('/')
    service         = parts[1].split('.') if len(parts) > 1 else ''.split('.')
    khaleesiGate    = service[1] if len(service) > 1 else ''
    khaleesiService = service[2] if len(service) > 2 else ''
    grpcService     = service[3] if len(service) > 3 else ''
    grpcMethod      = parts[2]   if len(parts) > 2   else ''
    return (
        self.stringOrUnknown(value = khaleesiGate),
        self.stringOrUnknown(value = khaleesiService),
        self.stringOrUnknown(value = grpcService),
        self.stringOrUnknown(value = grpcMethod),
    )

  def stringOrUnknown(self, *, value: str) -> str :
    """Either return the value, or UNKNOWN if empty."""
    if value:
      return value
    return 'UNKNOWN'
