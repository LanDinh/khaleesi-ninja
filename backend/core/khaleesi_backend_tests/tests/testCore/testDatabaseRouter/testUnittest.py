"""Test the database router."""

# Django.
from django.apps import apps

# khaleesi.ninja.
from khaleesi.core.database_router.unittest import TestDatabaseRouter
from khaleesi.core.testUtil.testCase import SimpleTestCase


class DatabaseRouterTestCase(SimpleTestCase):
  """Test the database router."""

  databaseRouter = TestDatabaseRouter()

  def testMigrateExactlyOnce(self) -> None :
    """Test the database performs exactly once for the database connections."""
    for app in apps.get_app_configs():
      with self.subTest(app = app.name):
        # Prepare data.
        count = 0
        # Execute test.
        for database in ['read', 'write']:
          result = self.databaseRouter.allow_migrate(database, app.name)
          if result:
            count += 1
        # Assert result.
        self.assertEqual(1, count)
