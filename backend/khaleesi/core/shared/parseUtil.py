"""Shared utility."""

# Python.
from datetime import datetime, timezone
from functools import partial
from typing import Callable, Any, Optional, TypeVar, List, Protocol


T_co = TypeVar('T_co', covariant = True)


def _parseInput(
    *,
    parser : Callable[[Any], T_co],
    raw    : Optional[Any],
    default: Optional[T_co],
    name   : str,
    errors : List[str],
) -> Optional[T_co] :
  """Attempt to parse the input."""
  try:
    if raw:
      return parser(raw)
    return default
  except (TypeError, ValueError) as exception:
    errors.append(f'{type(exception).__name__} parsing {name}: {str(exception)}.\n')
    return default

class Parser(Protocol[T_co]):
  """Signature for parsers."""
  def __call__(self, *, raw: Optional[Any], name: str, errors: List[str]) -> Optional[T_co] : ...


parseTimestamp: Parser[datetime] = partial(
  _parseInput,
  parser  = lambda x : x.replace(tzinfo = timezone.utc),
  default = datetime.min.replace(tzinfo = timezone.utc),
)
parseString: Parser[str] = partial(_parseInput, parser = lambda x : x, default = 'UNKNOWN')
