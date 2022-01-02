"""Test the parse utility."""

# Python.
from datetime import datetime, timezone
from uuid import uuid4

# khaleesi.ninja.
from khaleesi.core.test_util import SimpleTestCase
from microservice.parse_util import parse_uuid, parse_timestamp


class ParseUtilTestCase(SimpleTestCase):
  """Test the parse utility."""

  def test_parse_uuid(self) -> None :
    """Test valid input for parse_uuid."""
    # Prepare data.
    raw = uuid4()
    # Execute test.
    result, error = parse_uuid(raw = str(raw), name = 'valid_uuid')
    # Assert result.
    self.assertEqual(raw, result)
    self.assertEqual('', error)

  def test_parse_uuid_empty(self) -> None :
    """Test empty input for parse_uuid."""
    # Prepare data.
    raw = None
    # Execute test.
    result, error = parse_uuid(raw = raw, name = 'empty uuid')
    # Assert result.
    self.assertIsNone(result)
    self.assertEqual('', error)

  def test_parse_uuid_invalid(self) -> None :
    """Test invalid input for parse_uuid."""
    # Prepare data.
    name = 'invalid uuid'
    raw = 'invalid_uuid'
    # Execute test.
    result, error = parse_uuid(raw = raw, name = name)
    # Assert result.
    self.assertIsNone(result)
    self.assertNotEqual('', error)
    self.assertIn(name, error)

  def test_parse_timestamp(self) -> None :
    """Test valid input for parse_timestamp."""
    # Prepare data.
    for raw in [ datetime.now(tz = timezone.utc), datetime.now() ]:
      with self.subTest(raw = raw):
        # Execute test.
        result, error = parse_timestamp(raw = raw, name = 'valid_timestamp')
        # Assert result.
        self.assertEqual(raw.replace(tzinfo = None), result.replace(tzinfo = None))  # type: ignore[union-attr]  # pylint: disable=line-too-long
        self.assertEqual('', error)

  def test_parse_timestamp_empty(self) -> None :
    """Test invalid input for parse_timestamp."""
    # Prepare data.
    raw = None
    # Execute test.
    result, error = parse_timestamp(raw = raw, name = 'empty timestamp')
    # Assert result.
    self.assertEqual(datetime.min.replace(tzinfo = timezone.utc), result)
    self.assertEqual('', error)
