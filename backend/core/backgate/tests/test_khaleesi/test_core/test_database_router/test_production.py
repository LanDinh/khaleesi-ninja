"""Test the database router."""

# Django.
from django.apps import apps
from django.conf import settings

# khaleesi.ninja.
from khaleesi.core.database_router.production import DatabaseRouter
from khaleesi.core.test_util.test_case import SimpleTestCase


class DatabaseRouterTestCase(SimpleTestCase):
  """Test the database router."""

  database_router = DatabaseRouter()

  def test_db_for_read(self) -> None :
    """Test the database alias for reads."""
    for model in apps.get_models():
      with self.subTest(model = f'{model.__module__}.{model.__name__}'):
        # Execute test.
        result = self.database_router.db_for_read(model)
        # Assert result.
        self.assertEqual('read', result)

  def test_db_for_write(self) -> None :
    """Test the database alias for writes."""
    for model in apps.get_models():
      with self.subTest(model = f'{model.__module__}.{model.__name__}'):
        # Execute test.
        result = self.database_router.db_for_write(model)
        # Assert results
        self.assertEqual('write', result)

  def test_allow_migrate(self) -> None :
    """Test the database allows migrations to the migrations alias."""
    for app in apps.get_app_configs():
      with self.subTest(app = app.name):
        # Execute test.
        result = self.database_router.allow_migrate('migrate', app.name)
        # Assert result.
        self.assertTrue(result)

  def test_prohibit_migrate(self) -> None :
    """Test the database prohibits migrations for all aliases except 'migrate'."""
    for database in [database for database in settings.DATABASES.keys() if database != 'migrate']:
      for app in apps.get_app_configs():
        with self.subTest(database = database, app = app.name):
          # Execute test.
          result = self.database_router.allow_migrate(database, app.name)
          # Assert result.
          self.assertFalse(result)
