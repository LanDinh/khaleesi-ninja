"""The tests for the translation microservice."""

# khaleesi.ninja.
from base.test_util.test import CombinedTestCase
from translation.translate import translate_exception


class TranslationTests(CombinedTestCase):
  """Test translations."""

  def test_translate_exception(self) -> None :
    """Test exception translations."""
    # Prepare data.
    key = 'key'
    # Perform test.
    result = translate_exception(key = key)
    # Assert result.
    self.assertEqual(key, result)
