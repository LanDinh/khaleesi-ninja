"""Prepare handlers for the server."""

# Python.
from typing import Any, cast

# Django.
from django.utils.module_loading import import_string

# gRPC.
from grpc import Server

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LOGGER
from khaleesi.core.shared.exceptions import ProgrammingException


def importSetting(*, name: str, fullyQualifiedName: str, **kwargs: Any) -> Any :
  """Import something from the settings."""
  try:
    LOGGER.debug(f'Importing {name} {fullyQualifiedName}...')
    return import_string(fullyQualifiedName)(**kwargs)
  except ImportError as error:
    raise ProgrammingException(
      privateMessage = 'Could not import {name}.',
      privateDetails = fullyQualifiedName,
    ) from error


def registerService(*, rawHandler: str, server: Server) -> str :
  """Register the specified handler."""
  try:
    LOGGER.debug(f'Adding gRPC handler {rawHandler}...')
    handler = f'{rawHandler}.serviceConfiguration'
    serviceConfiguration = import_string(handler)
    serviceConfiguration.registerService(server)
    return cast(str, serviceConfiguration.name)
  except ImportError as error:
    raise ProgrammingException(
      privateMessage = 'Could not import gRPC handler.',
      privateDetails = rawHandler,
    ) from error
