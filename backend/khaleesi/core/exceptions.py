"""Custom exceptions."""

# Django.
from django.conf import settings

# gRPC.
from grpc import StatusCode


class KhaleesiException(Exception):
  """Base exception."""

  def __init__(
      self, *,
      status: StatusCode,
      gate: str,
      service: str,
      public_key: str,
      public_details: str,
      private_details: str,
  ) -> None :
    """Initialize the exception."""
    final_public_details = private_details if settings.DEBUG else public_details
    super().__init__(final_public_details)
    self.status = status
    self.gate = gate
    self.service = service
    self.public_key = public_key
    self.public_details = final_public_details
    self.private_details = private_details


class KhaleesiCoreException(KhaleesiException):
  """Base core exception."""

  def __init__(
      self, *,
      status: StatusCode,
      public_key: str,
      public_details: str,
      private_details: str,
  ) -> None :
    """Initialize the exception."""
    super().__init__(
      status = status,
      gate = 'core',
      service = 'core',
      public_key = public_key,
      public_details = public_details,
      private_details = private_details,
    )


class InvalidArgumentException(KhaleesiCoreException):
  """Invalid arguments."""

  def __init__(self, *, public_details: str = '', private_details: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status = StatusCode.INVALID_ARGUMENT,
      public_key = 'invalid-argument',
      public_details = public_details,
      private_details = private_details,
    )


class InternalServerException(KhaleesiCoreException):
  """Internal server errors."""

  def __init__(self, *, private_details: str) -> None :
    """Initialize the exception."""
    super().__init__(
      status = StatusCode.INTERNAL,
      public_key = 'internal-server-error',
      public_details = '',
      private_details = private_details,
    )
