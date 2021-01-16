"""The tests for the signals creating the base users and roles."""

# pylint: disable=line-too-long

# Python.
from unittest.mock import patch, MagicMock

# Django.
from django.apps import apps

# khaleesi.ninja
from settings.settings import UserNames
from test_util.test import SimpleTestCase, TestCase
from common.service_type import ServiceType
from common.models import Role, User
from common.signals.create_base_users_and_roles import create_base_users_and_roles


# noinspection PyUnresolvedReferences,PyTypeHints,PyTypeChecker,PyMissingOrEmptyDocstring,PyMethodMayBeStatic
class PostMigrateUnitTests(SimpleTestCase):
  """The unit tests for the post_migrate signals."""

  @patch.object(User.migrations, 'create_superuser')
  @patch.object(User.migrations, 'create_anonymous_user')
  @patch.object(Role.migrations, 'create')
  def test_create_base_users_and_roles_django(  # pylint: disable=no-self-use
      self,
      role: MagicMock,
      anonymous_user: MagicMock,
      superuser: MagicMock,
  ) -> None :
    """Test that nothing gets created."""
    # Prepare data.
    app_config = lambda: None
    app_config.name = 'test'  # type: ignore[attr-defined]
    # Perform test.
    create_base_users_and_roles(sender = app_config)
    # Assert result.
    role.assert_not_called()
    anonymous_user.assert_not_called()
    superuser.assert_not_called()

  def test_create_base_users_and_roles_base(self) -> None :  # pylint: disable=no-self-use
    """Test that only users get created."""
    with patch.object(User.migrations, 'create_superuser') as superuser:
      with patch.object(User.migrations, 'create_anonymous_user') as anonymous_user:
        with patch.object(Role.migrations, 'create') as role:
          # Prepare data.
          app_config = apps.get_app_config('common')
          # Perform test.
          create_base_users_and_roles(sender = app_config)
          # Assert result.
          role.assert_not_called()
          anonymous_user.assert_called_once_with()
          superuser.assert_called_once_with()

  def test_create_base_users_and_roles_khaleesi(self) -> None :  # pylint: disable=no-self-use
    """Test that only roles get created."""
    with patch.object(User.migrations, 'create_superuser') as superuser:
      with patch.object(User.migrations, 'create_anonymous_user') as anonymous_user:
        with patch.object(Role.migrations, 'create') as role:
          # Prepare data.
          app_config = apps.get_app_config('translate')
          # Perform test.
          create_base_users_and_roles(sender = app_config)
          # Assert result.
          superuser.assert_not_called()
          anonymous_user.assert_not_called()
          role.assert_called_with(service = ServiceType.TRANSLATE)


# noinspection PyMethodMayBeStatic
class PostMigrateIntegrationTests(TestCase):
  """The integration tests for the post_migrate signals."""

  def test_create_base_users_and_roles(self) -> None :  # pylint: disable=no-self-use
    """Test that users and roles get created successfully."""
    # Assert result.
    User.objects.get(username = UserNames.anonymous())
    User.objects.get(username = UserNames.superuser())
    for service in ServiceType:
      Role.objects.get(service = service.name)
