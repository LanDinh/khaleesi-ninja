"""Base test util for LogRequest."""

# Python.
from typing import Dict, Any

# Django.
from django.urls import ResolverMatch

# khaleesi.ninja.
from common.service_type import ServiceType


class TestLogRequestIntegrationMixin:
  """Base test util for LogRequest."""

  @staticmethod
  def create_and_get_minimum_input() -> Dict[str, Any] :
    """Minimum input for create_and_get."""
    return {
        'backend_request': ResolverMatch(
            func = lambda x: x,
            args = (),
            kwargs = {'backend': 'parameters'},
            url_name = 'backend_feature',
            route = 'backend_route',
            namespaces = ['TRANSLATE'],
        ),
        'backend_body': {'backend': 'body'},
        'frontend_route': 'frontend_route',
        'frontend_parameters': 'frontend_parameters',
        'frontend_service': ServiceType.TRANSLATE,
        'frontend_feature': 'frontend_feature',
        'frontend_body': 'frontend_body',
    }
