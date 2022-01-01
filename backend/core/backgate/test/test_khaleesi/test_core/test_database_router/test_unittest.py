"""Test the database router."""

# Django.
from django.apps import apps

# khaleesi.ninja.
from khaleesi.core.database_router.unittest import TestDatabaseRouter
from khaleesi.core.test_util import SimpleTestCase


class DatabaseRouterTestCase(SimpleTestCase):
  """Test the database router."""

  database_router = TestDatabaseRouter()

  def test_migrate_exactly_once(self) -> None :
    """Test the database performs exactly once for the database connections."""
    for app in apps.get_app_configs():
      with self.subTest(app = app.name):
        # Prepare data.
        count = 0
        # Execute tests.
        for database in ['read', 'write']:
          result = self.database_router.allow_migrate(database, app.name)
          if result:
            count += 1
        # Assert results.
        self.assertEqual(1, count)
