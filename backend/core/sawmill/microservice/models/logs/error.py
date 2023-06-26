"""Error logs."""

# Python.
from __future__ import annotations
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_sawmill_pb2 import Error as GrpcError, ErrorResponse as GrpcErrorResponse
from microservice.models.logs.abstract import Metadata


class ErrorManager(models.Manager['Error']):
  """Custom model manager."""

  def logError(self, *, grpcError: GrpcError) -> Error :
    """Log an error."""

    errors: List[str] = []

    error = {
        'errorId'  : parseString(raw = grpcError.id       , name = 'errorId'  , errors = errors),
        'status'   : parseString(raw = grpcError.status   , name = 'status'   , errors = errors),
        'loglevel' : parseString(raw = grpcError.loglevel , name = 'loglevel' , errors = errors),
        'gate'     : parseString(raw = grpcError.gate     , name = 'gate'     , errors = errors),
        'service'  : parseString(raw = grpcError.service  , name = 'service'  , errors = errors),
        'publicKey': parseString(raw = grpcError.publicKey, name = 'publicKey', errors = errors),
    }

    return self.create(
      **self.model.logMetadata(metadata = grpcError.requestMetadata, errors = errors),
      **error,
      publicDetails  = grpcError.publicDetails,
      privateMessage = grpcError.privateMessage,
      privateDetails = grpcError.privateDetails,
      stacktrace     = grpcError.stacktrace,
    )


class Error(Metadata):
  """Error logs."""
  errorId = models.TextField(default = 'UNKNOWN')

  status   = models.TextField(default = 'UNKNOWN')
  loglevel = models.TextField(default = 'FATAL')

  gate    = models.TextField(default = 'UNKNOWN')
  service = models.TextField(default = 'UNKNOWN')

  publicKey     = models.TextField(default = 'UNKNOWN')
  publicDetails = models.TextField(default = '')

  privateMessage = models.TextField(default = '')
  privateDetails = models.TextField(default = '')
  stacktrace     = models.TextField(default = '')

  objects = ErrorManager()

  def toGrpc(self) -> GrpcErrorResponse :
    """Map to gRPC event message."""

    grpcErrorResponse = GrpcErrorResponse()
    # Request metadata.
    self.requestMetadataToGrpc(requestMetadata = grpcErrorResponse.error.requestMetadata)
    self.responseMetadataToGrpc(responseMetadata = grpcErrorResponse.errorMetadata)
    grpcErrorResponse.error.id = self.errorId
    # Error.
    grpcErrorResponse.error.status         = self.status
    grpcErrorResponse.error.loglevel       = self.loglevel
    grpcErrorResponse.error.gate           = self.gate
    grpcErrorResponse.error.service        = self.service
    grpcErrorResponse.error.publicKey      = self.publicKey
    grpcErrorResponse.error.publicDetails  = self.publicDetails
    grpcErrorResponse.error.privateMessage = self.privateMessage
    grpcErrorResponse.error.privateDetails = self.privateDetails
    grpcErrorResponse.error.stacktrace     = self.stacktrace

    return grpcErrorResponse
