"""Shared utility."""

# Python.
from datetime import datetime, timezone
from typing import Callable, Any, Tuple, Optional, TypeVar
from uuid import UUID


T = TypeVar('T')  # pylint: disable=invalid-name


def _parse_input(
    *,
    parser: Callable[[Any], T],
    raw: Optional[Any],
    default: Optional[T],
    name: str,
) -> Tuple[Optional[T], str] :
  """Attempt to parse the input."""
  try:
    if raw:
      return parser(raw), ''
    return default, ''
  except (TypeError, ValueError) as exception:
    return default, f'{type(exception).__name__} parsing {name}: {str(exception)}.\n'

def parse_uuid(*, raw: Optional[str], name: str) -> Tuple[Optional[UUID], str]:
  """Attempt to parse UUIDs."""
  return _parse_input(
    parser = UUID,
    raw = raw,
    default = None,
    name = name,
  )

def parse_timestamp(*, raw: Optional[datetime], name: str) -> Tuple[Optional[datetime], str]:
  """Attempt to parse UUIDs."""
  def parser(parser_input: datetime) -> datetime :
    """Custom parser."""
    return parser_input.replace(tzinfo = timezone.utc)
  return _parse_input(
    parser = parser,
    raw = raw,
    default = datetime.min.replace(tzinfo = timezone.utc),
    name = name,
  )
