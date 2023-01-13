"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from typing import List

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.parse_util import parse_timestamp, parse_string


class ParseUtilTestCase(SimpleTestCase):
  """Test the parse utility."""

  def test_parse_timestamp(self) -> None :
    """Test valid input for parse_timestamp."""
    # Prepare data.
    errors: List[str] = []
    for raw in [ datetime.now(tz = timezone.utc), datetime.now() ]:
      with self.subTest(raw = raw):
        # Execute test.
        result = parse_timestamp(raw = raw, name = 'valid_timestamp', errors = errors)
        # Assert result.
        self.assertEqual(raw.replace(tzinfo = None), result.replace(tzinfo = None))  # type: ignore[union-attr]  # pylint: disable=line-too-long
        self.assertEqual(0                         , len(errors))

  def test_parse_timestamp_empty(self) -> None :
    """Test empty input for parse_timestamp."""
    # Prepare data.
    raw = None
    errors: List[str] = []
    # Execute test.
    result = parse_timestamp(raw = raw, name = 'empty_timestamp', errors = errors)
    # Assert result.
    self.assertEqual(datetime.min.replace(tzinfo = timezone.utc), result)
    self.assertEqual(0                                          , len(errors))

  def test_parse_timestamp_invalid(self) -> None :
    """Test empty input for parse_timestamp."""
    # Prepare data.
    raw = 'not-a-timestamp'
    errors: List[str] = []
    # Execute test.
    result = parse_timestamp(raw = raw, name = 'invalid_timestamp', errors = errors)
    # Assert result.
    self.assertEqual(datetime.min.replace(tzinfo = timezone.utc), result)
    self.assertEqual(1                                          , len(errors))

  def test_parse_string(self) -> None :
    """Test valid input for parse_timestamp."""
    # Prepare data.
    errors: List[str] = []
    raw = 'string'
    # Execute test.
    result = parse_string(raw = raw, name = 'valid_string', errors = errors)
    # Assert result.
    self.assertEqual(raw, result)
    self.assertEqual(0  , len(errors))

  def test_parse_string_empty(self) -> None :
    """Test empty input for parse_timestamp."""
    # Prepare data.
    raw = None
    errors: List[str] = []
    # Execute test.
    result = parse_string(raw = raw, name = 'empty_string', errors = errors)
    # Assert result.
    self.assertEqual('UNKNOWN', result)
    self.assertEqual(0        , len(errors))
