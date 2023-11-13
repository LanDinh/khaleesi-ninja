"""Basic broom for the maid."""

# Python.
from abc import ABC, abstractmethod
from typing import cast

# Django.
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.grpc.importUtil import importSetting
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.settings.definition import KhaleesiNinjaSettings
from khaleesi.proto.core_pb2 import JobExecutionRequest, EmptyResponse


khaleesiSettings: KhaleesiNinjaSettings = settings.KHALEESI_NINJA


class BaseBroom(ABC):
  """Basic broom for the maid."""

  @abstractmethod
  def cleanup(self, *, jobExecutionRequest: JobExecutionRequest) -> EmptyResponse :
    """Initiate cleanup."""


class Broom(BaseBroom):
  """No-op broom."""

  def cleanup(self, *, jobExecutionRequest: JobExecutionRequest) -> EmptyResponse :
    """Do nothing."""
    return EmptyResponse()


def instantiateBroom() -> BaseBroom :
  """Instantiate the broom."""
  LOGGER.info('Importing broom...')
  return cast(BaseBroom, importSetting(
    name               = 'broom',
    fullyQualifiedName = khaleesiSettings['SINGLETONS']['BROOM']['NAME'],
  ))
