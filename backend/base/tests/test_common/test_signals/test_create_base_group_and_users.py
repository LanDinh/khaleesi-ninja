"""The tests for the post_migrate signals."""

# Python.
from unittest.mock import patch, MagicMock, call

# Django.
from django.apps import apps

# khaleesi.ninja
from settings.settings import Settings
from test_util.test import SimpleTestCase, TestCase
from common.models import Group, User
from common.signals.create_base_groups_and_users import create_base_groups_and_users


class PostMigrateUnitTests(SimpleTestCase):
  """The unit tests for the post_migrate signals."""


  @patch.object(User.migrations, 'create_superuser')
  @patch.object(User.migrations, 'create_anonymous_user')
  @patch.object(Group.migrations, 'create')
  def test_create_base_groups_and_users_django(  # pylint: disable=no-self-use
      self,
      group: MagicMock,
      anonymous_user: MagicMock,
      superuser: MagicMock,
  ) -> None :
    """Test if no groups nor permissions get created."""
    # Prepare data.
    app_config = lambda: None
    # noinspection PyTypeHints,PyUnresolvedReferences
    app_config.name = 'test'  # type: ignore[attr-defined]
    # Perform test.
    # noinspection PyTypeChecker
    create_base_groups_and_users(sender = app_config)
    # Assert result.
    group.assert_not_called()
    anonymous_user.assert_not_called()
    superuser.assert_not_called()

  @patch.object(User.migrations, 'create_superuser')
  @patch.object(User.migrations, 'create_anonymous_user')
  @patch.object(Group.migrations, 'create')
  def test_create_base_groups_and_users_khaleesi(  # pylint: disable=no-self-use
      self,
      group: MagicMock,
      anonymous_user: MagicMock,
      superuser: MagicMock,
  ) -> None :
    """Test if groups and permissions get created successfully."""
    # Prepare data.
    app_config = apps.get_app_config('common')
    # Perform test.
    create_base_groups_and_users(sender = app_config)
    # Assert result.
    superuser.assert_called_once_with()
    anonymous_user.assert_called_once_with()
    group.assert_has_calls([
        call(name = Settings.dragon_groupname()),
        call(name = Settings.warg_groupname()),
        call(name = Settings.missandei_groupname()),
    ])


class PostMigrateIntegrationTests(TestCase):
  """The integration tests for the post_migrate signals."""

  # noinspection PyMethodMayBeStatic
  def test_create_base_groups_and_users(self) -> None :  # pylint: disable=no-self-use
    """Test if groups and permissions get created successfully."""
    # Assert result.
    User.objects.get(username = Settings.anonymous_username())
    User.objects.get(username = Settings.khaleesi_username())
    Group.objects.get(name = Settings.dragon_groupname())
    Group.objects.get(name = Settings.warg_groupname())
    Group.objects.get(name = Settings.missandei_groupname())
