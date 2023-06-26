"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from typing import List

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.core.shared.parseUtil import parseTimestamp, parseString


class ParseUtilTestCase(SimpleTestCase):
  """Test the parse utility."""

  def testParseTimestamp(self) -> None :
    """Test valid input for parseTimestamp."""
    # Prepare data.
    errors: List[str] = []
    for raw in [ datetime.now(tz = timezone.utc), datetime.now() ]:
      with self.subTest(raw = raw):
        # Execute test.
        result = parseTimestamp(raw = raw, name = 'valid-timestamp', errors = errors)
        # Assert result.
        self.assertEqual(raw.replace(tzinfo = None), result.replace(tzinfo = None))  # type: ignore[union-attr]  # pylint: disable=line-too-long
        self.assertEqual(0                         , len(errors))

  def testParseTimestampEmpty(self) -> None :
    """Test empty input for parseTimestamp."""
    # Prepare data.
    raw = None
    errors: List[str] = []
    # Execute test.
    result = parseTimestamp(raw = raw, name = 'empty-timestamp', errors = errors)
    # Assert result.
    self.assertEqual(datetime.min.replace(tzinfo = timezone.utc), result)
    self.assertEqual(0                                          , len(errors))

  def testParseTimestampInvalid(self) -> None :
    """Test empty input for parseTimestamp."""
    # Prepare data.
    raw = 'not-a-timestamp'
    errors: List[str] = []
    # Execute test.
    result = parseTimestamp(raw = raw, name = 'invalid-timestamp', errors = errors)
    # Assert result.
    self.assertEqual(datetime.min.replace(tzinfo = timezone.utc), result)
    self.assertEqual(1                                          , len(errors))

  def testParseString(self) -> None :
    """Test valid input for parseTimestamp."""
    # Prepare data.
    errors: List[str] = []
    raw = 'string'
    # Execute test.
    result = parseString(raw = raw, name = 'valid-string', errors = errors)
    # Assert result.
    self.assertEqual(raw, result)
    self.assertEqual(0  , len(errors))

  def testParseStringEmpty(self) -> None :
    """Test empty input for parseTimestamp."""
    # Prepare data.
    raw = None
    errors: List[str] = []
    # Execute test.
    result = parseString(raw = raw, name = 'empty-string', errors = errors)
    # Assert result.
    self.assertEqual('UNKNOWN', result)
    self.assertEqual(0        , len(errors))
