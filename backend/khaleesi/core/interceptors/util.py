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
    parts      = raw.split('/')
    rawService = parts[1].split('.') if len(parts) > 1 else ''.split('.')
    site       = rawService[1] if len(rawService) > 1 else ''
    app        = rawService[2] if len(rawService) > 2 else ''
    service    = rawService[3] if len(rawService) > 3 else ''
    method     = parts[2]   if len(parts) > 2   else ''
    return (
        self.stringOrUnknown(value = site),
        self.stringOrUnknown(value = app),
        self.stringOrUnknown(value = service),
        self.stringOrUnknown(value = method),
    )

  def stringOrUnknown(self, *, value: str) -> str :
    """Either return the value, or UNKNOWN if empty."""
    if value:
      return value
    return 'UNKNOWN'
