"""Prepare handlers for the server."""

# Python.
from typing import Any, cast

# Django.
from django.utils.module_loading import import_string

# gRPC.
from grpc import Server

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LOGGER
from khaleesi.core.shared.exceptions import ProgrammingException


def import_setting(*, name: str, fully_qualified_name: str, **kwargs: Any) -> Any :
  """Import something from the settings."""
  try:
    LOGGER.debug(f'Importing {name} {fully_qualified_name}...')
    return import_string(fully_qualified_name)(**kwargs)
  except ImportError as error:
    raise ProgrammingException(
      private_message = 'Could not import {name}.',
      private_details = fully_qualified_name,
    ) from error


def register_service(*, raw_handler: str, server: Server) -> str :
  """Register the specified handler."""
  try:
    LOGGER.debug(f'Adding gRPC handler {raw_handler}...')
    handler = f'{raw_handler}.service_configuration'
    service_configuration = import_string(handler)
    service_configuration.register_service(server)
    return cast(str, service_configuration.name)
  except ImportError as error:
    raise ProgrammingException(
      private_message = 'Could not import gRPC handler.',
      private_details = raw_handler,
    ) from error
