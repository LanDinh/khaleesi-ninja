"""Default Manager."""

# Python.
import json
from typing import Optional, Dict, Any
from uuid import UUID

# Django.
from django.urls import ResolverMatch

# khaleesi.ninja.
from common.language_type import Language
from common.models.manager import  Manager, T
from common.service_type import ServiceType


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences,PyTypeHints
class DefaultManager(Manager[T]):
  """Default Manager."""

  def create_and_get(
      self, *,
      # Client information.
      client_id: Optional[UUID] = None,
      language: Optional[Language] = None,
      # Request information backend.
      backend_request: ResolverMatch,
      backend_body: Dict[str, Any],
      # Request information frontend.
      frontend_route: str,
      frontend_parameters: str,
      frontend_service: ServiceType,
      frontend_feature: str,
      frontend_body: str,
  ) -> T :
    """Create a new request log."""
    log = self.model(
        # Backend.
        backend_route = backend_request.route,
        backend_parameters = json.dumps(backend_request.kwargs),
        backend_service = backend_request.namespace,
        backend_feature = backend_request.url_name,
        backend_body = json.dumps(backend_body),
        # Frontend.
        frontend_route = frontend_route,
        frontend_parameters = frontend_parameters,
        frontend_service = frontend_service.name,
        frontend_feature = frontend_feature,
        frontend_body = frontend_body,
    )
    if client_id:
      log.client_id = client_id  # type: ignore[attr-defined]
    if language:
      log.language = language.name  # type: ignore[attr-defined]
    log.save()
    return log
