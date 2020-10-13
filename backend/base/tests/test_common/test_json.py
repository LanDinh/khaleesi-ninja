"""Test the custom json encoder."""

# Python.
from dataclasses import dataclass
from unittest.mock import patch, MagicMock

# Django.
from django.core.serializers.json import DjangoJSONEncoder

# khaleesi.ninja.
from common.json import JSONEncoder
from common.test.test import SimpleTestCase, TestCase


@dataclass
class TestDataClass:
  """Some data class for testing."""
  some_attribute: str = 'test'


class JSONEncoderUnitTests(SimpleTestCase):
  """Test the custom json encoder."""
  encoder = JSONEncoder()

  def test_dataclass_encoding(self) -> None :
    """Make sure that dataclasses can be encoded."""
    test = TestDataClass()
    self.encoder.default(o = test)

  @patch.object(DjangoJSONEncoder, 'default')
  def test_default_encoding(self, _: MagicMock) -> None :
    """Make sure that regular encoding still works."""
    self.encoder.default(o = 'test')


class JSONEncoderIntegrationTests(TestCase):
  """Test the custom json encoder."""
  encoder = JSONEncoder()

  def test_dataclass_encoding(self) -> None :
    """Make sure that dataclasses can be encoded."""
    test = TestDataClass()
    self.encoder.default(o = test)
