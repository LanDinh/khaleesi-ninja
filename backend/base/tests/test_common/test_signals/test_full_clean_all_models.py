"""The tests for the signals full cleaning all models."""

# Python.
from unittest.mock import MagicMock

# Django.
from django.apps import apps
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError

# khaleesi.ninja.
from common.signals.full_clean_all_models import full_clean_all_models
from test_util.test import SimpleTestCase, TestCase

# pylint: disable=line-too-long


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
          if hasattr(sender.objects, '_get_queryset'):
            sender.objects._get_queryset().create() # type: ignore[attr-defined]
          else:
            sender.objects.get_queryset().create()

  def test_no_default_permissions(self) -> None :
    """Test if default permissions are prevented from being created."""
    for permission in Permission.objects.all():
      with self.subTest(permission = permission):
        for code in ['add', 'change', 'delete', 'view']:
          self.assertNotRegex(permission.codename, f'{code}_[a-zA-Z]*')
          self.assertNotRegex(permission.name, f'Can {code} [a-zA-Z]*')
        self.assertEqual(permission.codename, permission.name)
