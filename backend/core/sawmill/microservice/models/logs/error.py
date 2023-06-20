"""Error logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parse_util import parse_string
from khaleesi.proto.core_sawmill_pb2 import Error as GrpcError, ErrorResponse as GrpcErrorResponse
from microservice.models.logs.abstract import Metadata


class ErrorManager(models.Manager['Error']):
  """Custom model manager."""

  def log_error(self, *, grpc_error: GrpcError) -> Error :
    """Log an error."""

    errors: List[str] = []

    error = {
        'error_id'  : parse_string(raw = grpc_error.id       , name = 'error_id', errors = errors),
        'status'    : parse_string(raw = grpc_error.status   , name = 'status'  , errors = errors),
        'loglevel'  : parse_string(raw = grpc_error.loglevel , name = 'loglevel', errors = errors),
        'gate'      : parse_string(raw = grpc_error.gate     , name = 'gate'    , errors = errors),
        'service'   : parse_string(raw = grpc_error.service  , name = 'service' , errors = errors),
        'public_key': parse_string(
          raw = grpc_error.publicKey,
          name = 'public_key',
          errors = errors,
        ),
    }

    return self.create(
      **self.model.log_metadata(metadata = grpc_error.requestMetadata, errors = errors),
      **error,
      public_details  = grpc_error.publicDetails,
      private_message = grpc_error.privateMessage,
      private_details = grpc_error.privateDetails,
      stacktrace      = grpc_error.stacktrace,
    )


class Error(Metadata):
  """Error logs."""
  error_id = models.TextField(default = 'UNKNOWN')

  status   = models.TextField(default = 'UNKNOWN')
  loglevel = models.TextField(default = 'FATAL')

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
    self.request_metadata_to_grpc(request_metadata = grpc_error_response.error.requestMetadata)
    self.response_metadata_to_grpc(response_metadata = grpc_error_response.errorMetadata)
    grpc_error_response.error.id = self.error_id
    # Error.
    grpc_error_response.error.status         = self.status
    grpc_error_response.error.loglevel       = self.loglevel
    grpc_error_response.error.gate           = self.gate
    grpc_error_response.error.service        = self.service
    grpc_error_response.error.publicKey      = self.public_key
    grpc_error_response.error.publicDetails  = self.public_details
    grpc_error_response.error.privateMessage = self.private_message
    grpc_error_response.error.privateDetails = self.private_details
    grpc_error_response.error.stacktrace     = self.stacktrace

    return grpc_error_response
