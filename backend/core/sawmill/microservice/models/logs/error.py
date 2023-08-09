"""Error logs."""

from __future__ import annotations

# Python.
from typing import List

# Django.
from django.db import models

# khaleesi.ninja.
from khaleesi.core.models.baseModel import Manager
from khaleesi.core.models.idModel import Model
from khaleesi.core.shared.parseUtil import parseString
from khaleesi.proto.core_pb2 import ObjectMetadata
from khaleesi.proto.core_sawmill_pb2 import ErrorRequest as GrpcErrorRequest
from microservice.models.logs.metadataMixin import GrpcMetadataMixin


class Error(Model[GrpcErrorRequest], GrpcMetadataMixin):
  """Error logs."""
  khaleesiId = models.TextField(unique = False, editable = False)  # Avoid index building.

  status   = models.TextField(default = 'UNKNOWN')
  loglevel = models.TextField(default = 'FATAL')

  site = models.TextField(default = 'UNKNOWN')
  app  = models.TextField(default = 'UNKNOWN')

  publicKey     = models.TextField(default = 'UNKNOWN')
  publicDetails = models.TextField(default = '')

  privateMessage = models.TextField(default = '')
  privateDetails = models.TextField(default = '')
  stacktrace     = models.TextField(default = '')

  objects: Manager[Error]  # type: ignore[assignment]


  def khaleesiSave(
      self, *,
      metadata: ObjectMetadata = ObjectMetadata(),
      grpc    : GrpcErrorRequest,
      dbSave  : bool = True,
  ) -> None :
    """Change own values according to the grpc object."""
    errors: List[str] = []

    if self._state.adding:
      self.status    = parseString(raw = grpc.error.status   , name = 'status'   , errors = errors)
      self.loglevel  = parseString(raw = grpc.error.loglevel , name = 'loglevel' , errors = errors)
      self.site      = parseString(raw = grpc.error.site     , name = 'site'     , errors = errors)
      self.app       = parseString(raw = grpc.error.app      , name = 'app'      , errors = errors)
      self.publicKey = parseString(raw = grpc.error.publicKey, name = 'publicKey', errors = errors)
      self.publicDetails  = grpc.error.publicDetails
      self.privateMessage = grpc.error.privateMessage
      self.privateDetails = grpc.error.privateDetails
      self.stacktrace     = grpc.error.stacktrace

    # Needs to be at the end because it saves errors to the model.
    self.metadataFromGrpc(grpc = grpc.requestMetadata, errors = errors)
    super().khaleesiSave(metadata = metadata, grpc = grpc, dbSave = dbSave)

  def toGrpc(self) -> GrpcErrorRequest :
    """Return a grpc object containing own values."""
    grpc = GrpcErrorRequest()
    self.metadataToGrpc(logMetadata = grpc.logMetadata, requestMetadata = grpc.requestMetadata)

    # Error.
    grpc.error.status         = self.status
    grpc.error.loglevel       = self.loglevel
    grpc.error.site           = self.site
    grpc.error.app            = self.app
    grpc.error.publicKey      = self.publicKey
    grpc.error.publicDetails  = self.publicDetails
    grpc.error.privateMessage = self.privateMessage
    grpc.error.privateDetails = self.privateDetails
    grpc.error.stacktrace     = self.stacktrace

    return grpc
