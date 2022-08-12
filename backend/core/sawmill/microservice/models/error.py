"""Error logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.proto.core_sawmill_pb2 import Error as GrpcError, ErrorResponse as GrpcErrorResponse
from microservice.models.abstract import Metadata
from microservice.parse_util import parse_string


class ErrorManager(models.Manager['Error']):
  """Custom model manager."""

  def log_error(self, *, grpc_error: GrpcError) -> Error :
    """Log an error."""

    errors: List[str] = []

    error = {
        'status'     : parse_string(raw = grpc_error.status , name = 'status' , errors = errors),
        'gate'       : parse_string(raw = grpc_error.gate   , name = 'gate'   , errors = errors),
        'service'    : parse_string(raw = grpc_error.service, name = 'service', errors = errors),
        'public_key' : parse_string(
          raw = grpc_error.public_key,
          name = 'public_key',
          errors = errors,
        ),
    }

    return self.create(
      **self.model.log_metadata(metadata = grpc_error.request_metadata, errors = errors),
      **error,
      public_details = grpc_error.public_details,
      private_message = grpc_error.private_message,
      private_details = grpc_error.private_details,
      stacktrace = grpc_error.stacktrace,
    )


class Error(Metadata):
  """Error logs."""

  status = models.TextField(default = 'UNKNOWN')

  gate    = models.TextField(default = 'UNKNOWN')
  service = models.TextField(default = 'UNKNOWN')

  public_key     = models.TextField(default = 'UNKNOWN')
  public_details = models.TextField(default = '')

  private_message = models.TextField(default = '')
  private_details = models.TextField(default = '')
  stacktrace      = models.TextField(default = '')

  objects = ErrorManager()

  def to_grpc_error_response(self) -> GrpcErrorResponse :
    """Map to gRPC event message."""

    grpc_error_response = GrpcErrorResponse()
    # Request metadata.
    self.request_metadata_to_grpc(request_metadata = grpc_error_response.error.request_metadata)
    self.response_metadata_to_grpc(response_metadata = grpc_error_response.error_metadata)
    # Error.
    grpc_error_response.error.status          = self.status
    grpc_error_response.error.gate            = self.gate
    grpc_error_response.error.service         = self.service
    grpc_error_response.error.public_key      = self.public_key
    grpc_error_response.error.public_details  = self.public_details
    grpc_error_response.error.private_message = self.private_message
    grpc_error_response.error.private_details = self.private_details
    grpc_error_response.error.stacktrace      = self.stacktrace

    return grpc_error_response
