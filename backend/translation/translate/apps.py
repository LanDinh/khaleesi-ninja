"""The translate config."""

# Python.
from typing import List

# khaleesi.ninja.
from common.app_config import ServiceConfig
from common.service_type import ServiceType


class BaseConfig(ServiceConfig):
  """The translate config."""
  service = ServiceType.TRANSLATE
  roles: List[str] = []


class TranslateConfig(BaseConfig):
  """The translate config."""
  name = 'translate'

class CommonConfig(BaseConfig):
  """The translate config."""
  name = 'translation.translate'
