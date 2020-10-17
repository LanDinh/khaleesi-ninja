"""The tests for the custom signals."""

# Python.
from unittest.mock import MagicMock

# Django.
from django.apps import apps
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError

# khaleesi.ninja.
from common.signals import full_clean_all_models
from test_util.test import SimpleTestCase, TestCase

# pylint: disable=line-too-long


class SignalUnitTests(SimpleTestCase):
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


class SignalIntegrationTests(TestCase):
  """The integration tests for signal handling."""

  def test_full_clean_all_models(self) -> None :
    """Test if models enforce full clean."""
    for sender in [s for s in apps.get_models() if s._meta.managed]:  # pylint: disable=protected-access
      with self.subTest(sender = sender):
        with self.assertRaises(ValidationError):
          # If full_clean gets called, validation is applied.
          sender.objects.create()

  def test_no_default_permissions(self) -> None :
    """Test if default permissions are prevented from being created."""
    for permission in Permission.objects.all():
      with self.subTest(permission = permission):
        for code in ['add', 'change', 'delete', 'view']:
          self.assertNotRegex(
              permission.codename,
              '{code}_[a-zA-Z]*'.format(code = code),
          )
          self.assertNotRegex(
              permission.name,
              'Can {code} [a-zA-Z]*'.format(code = code)
          )
        self.assertEqual(permission.codename, permission.name)
