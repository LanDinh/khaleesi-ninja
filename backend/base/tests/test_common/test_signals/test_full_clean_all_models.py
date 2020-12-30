"""The tests for the signals full cleaning all models."""

# pylint: disable=line-too-long

# Python.
from unittest.mock import MagicMock

# Django.
from django.apps import apps
from django.core.exceptions import ValidationError

# khaleesi.ninja.
from common.signals.full_clean_all_models import full_clean_all_models
from test_util.test import SimpleTestCase, TestCase


class FullCleanAllModelsUnitTests(SimpleTestCase):
  """The unit tests for signal handling."""

  def test_full_clean_all_models(self) -> None :
    """Test if models enforce full clean."""
    for sender in [s for s in apps.get_models() if s._meta.managed]:  # pylint: disable=protected-access
      with self.subTest(sender = sender):
        # Initialize mocks.
        instance = MagicMock()
        instance.full_clean = MagicMock()
        # Run the method.
        full_clean_all_models(sender = sender, instance = instance)
        # Assert the result.
        instance.full_clean.assert_called_once_with(validate_unique = False)


# noinspection PyUnresolvedReferences,PyMissingOrEmptyDocstring
class FullCleanAllModelsIntegrationTests(TestCase):
  """The integration tests for signal handling."""

  def test_full_clean_all_models(self) -> None :
    """Test if models enforce full clean."""
    for sender in [
        s for s in apps.get_models()
        if not hasattr(s, 'TestMeta') or not s.TestMeta.testing  # type: ignore[attr-defined]
    ]:  # pylint: disable=protected-access
      with self.subTest(sender = sender):
        with self.assertRaises(ValidationError):
          # If full_clean gets called, validation is applied.
          sender.objects.get_queryset().create()
