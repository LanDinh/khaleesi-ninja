"""Khaleesi commands."""

# Python.
from abc import ABC, abstractmethod
from typing import Any

# Django.
from django.core.management.base import BaseCommand as DjangoBaseCommand

# khaleesi.ninja.
from khaleesi.core.logging.query_logger import query_logger
from khaleesi.core.logging.text_logger import STDOUT_WRITER, STDERR_WRITER


class BaseCommand(DjangoBaseCommand, ABC):
  """Base command."""

  def __init__(self) -> None :
    """Configure the logger."""
    super().__init__(stdout = STDOUT_WRITER, stderr = STDERR_WRITER)  # type: ignore[arg-type]
    self.stdout.ending = ''
    self.stderr.ending = ''

  def handle(self, *args: Any, **options: Any) -> None :
    """Make sure that all management commands use the query logger."""
    with query_logger():
      self.khaleesi_handle(*args, **options)

  @abstractmethod
  def khaleesi_handle(self, *args: Any, **options: Any) -> None :
    """Handle the command."""
