"""Test if no default permissions get created."""

# Django.
from django.contrib.auth.models import Permission

# khaleesi.ninja.
from test_util.test import TestCase


class FullCleanAllModelsIntegrationTests(TestCase):
  """The integration tests for signal handling."""

  def test_no_default_permissions(self) -> None :
    """Test if default permissions are prevented from being created."""
    for permission in Permission.objects.all():
      with self.subTest(permission = permission):
        for code in ['add', 'change', 'delete', 'view']:
          self.assertNotRegex(permission.codename, f'{code}_[a-zA-Z]*')
          self.assertNotRegex(permission.name, f'Can {code} [a-zA-Z]*')
        self.assertEqual(permission.codename, permission.name)
