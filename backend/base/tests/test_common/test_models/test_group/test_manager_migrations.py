"""The tests for the custom Group MigrationManager."""

# pylint: disable=line-too-long

# Python.
from dataclasses import dataclass, field
from typing import cast, Optional, List, Callable, Dict, Any
from unittest.mock import patch, MagicMock

# Django.
from django.contrib.auth.models import Permission, PermissionManager
from django.contrib.contenttypes.models import ContentType

# khaleesi.ninja
from common.models.group import Group, GroupType
from common.models.manager import BaseManager
from settings.settings import Settings
from test_util.models.group import TestGroupUnitMixin
from test_util.test import  SimpleTestCase, TestCase


@dataclass
class GroupTestType:
  """The type for the sub test cases."""
  group_type: GroupType
  # noinspection PyUnresolvedReferences
  method: Callable  # type: ignore[type-arg]
  name: str
  extra_arguments: Dict[str, Any] = field(default_factory = lambda: {})
  extra_permissions: List[str] = field(default_factory = lambda: [])


class GroupMigrationManagerUnitTests(SimpleTestCase, TestGroupUnitMixin):
  """The unit tests for the MigrationManager."""

  label = 'test'
  permissions = ['test']

  @patch.object(BaseManager, '_get_queryset', return_value = MagicMock())
  @patch.object(PermissionManager, 'filter')
  def test_update_or_create_groups(
      self,
      permission: MagicMock,
      base_queryset: MagicMock,
  ) -> None :
    """Test the group creation methods."""
    group_test_type: GroupTestType
    for group_test_type in [
        GroupTestType(
            group_type = GroupType.ANONYMOUS,
            method = Group.migrations.update_or_create_anonymous,
            name = Settings.anonymous_suffix(),
        ),
        GroupTestType(
            group_type = GroupType.AUTHENTICATED,
            method = Group.migrations.update_or_create_authenticated,
            name = Settings.authenticated_suffix(),
        ),
        GroupTestType(
            group_type = GroupType.DRAGON,
            method = Group.migrations.update_or_create_dragon,
            name = Settings.dragon_suffix(),
            extra_permissions = [Settings.authenticated_suffix(), Settings.anonymous_suffix()],
        ),
        GroupTestType(
            group_type = GroupType.CUSTOM,
            method = Group.migrations.update_or_create_custom,
            name = 'test',
            extra_arguments = {'name': 'test'},
        ),
    ]:
      with self.subTest(group_type = group_test_type.group_type):
        # Prepare data.
        group = cast(MagicMock, self.create_unit_group())
        group_create = MagicMock(return_value = [group, None])
        base_queryset.return_value.update_or_create = group_create
        # Perform test.
        group_test_type.method(
            label = self.label,
            permissions = self.permissions,
            **group_test_type.extra_arguments,
        )
        # Assert result.
        self.assert_group(
            group_create = group_create,
            permission = permission,
            group = group,
            name = group_test_type.name,
            group_type = group_test_type.group_type,
            permissions = group_test_type.extra_permissions,
        )
        permission.reset_mock()

  def assert_group(
      self, *,
      group_create: MagicMock,
      permission: MagicMock,
      group: MagicMock,
      name: str,
      group_type: GroupType,
      permissions: List[str],
  ) -> None :
    """Assert the group has the single specified permission."""
    group_create.assert_called_once_with(
        name = f'{self.label}.{name}',
        defaults = {'group_type': group_type},
    )
    group.permissions.set.assert_called_once()
    permission.assert_called_once_with(
        codename__in = self.permissions + permissions,
        content_type__app_label = self.label,
    )


class GroupMigrationManagerIntegrationTests(TestCase):
  """The integration tests for the MigrationManager."""

  label = 'test'
  permission_name = 'permission'
  content_type: Optional[ContentType] = None
  permission_object: Optional[Permission] = None

  def setUp(self) -> None :
    """Create permissions."""
    content_type, _ = ContentType.objects.get_or_create(
        model = Settings.permission_model(),
        app_label = self.label,
    )
    self.content_type = content_type

  def tearDown(self) -> None :
    """Cleanup permissions."""
    self.content_type = None
    self.permission_object = None

  def test_update_or_create_groups(self) -> None :
    """Test the group creation methods."""
    group_test_type: GroupTestType
    for group_test_type in [
        GroupTestType(
            group_type = GroupType.ANONYMOUS,
            method = Group.migrations.update_or_create_anonymous,
            name = Settings.anonymous_suffix(),
        ),
        GroupTestType(
            group_type = GroupType.AUTHENTICATED,
            method = Group.migrations.update_or_create_authenticated,
            name = Settings.authenticated_suffix(),
        ),
        GroupTestType(
            group_type = GroupType.DRAGON,
            method = Group.migrations.update_or_create_dragon,
            name = Settings.dragon_suffix(),
            extra_permissions = [Settings.authenticated_suffix(), Settings.anonymous_suffix()],
        ),
        GroupTestType(
            group_type = GroupType.CUSTOM,
            method = Group.migrations.update_or_create_custom,
            name = 'test',
            extra_arguments = {'name': 'test'},
        ),
    ]:
      with self.subTest(group_type = group_test_type.group_type):
        # Prepare data.
        self.permission_object = self.create_permission(name = self.permission_name)
        for permission in group_test_type.extra_permissions:
          self.create_permission(name = permission)
        # Perform test.
        group_test_type.method(
            label = self.label,
            permissions = [self.permission_name],
            **group_test_type.extra_arguments,
        )
        # Assert result.
        self.assert_group(
            group_type = group_test_type.group_type,
            name = group_test_type.name,
            permissions = group_test_type.extra_permissions,
        )
        Permission.objects.all().delete()

  def assert_group(self, *, group_type: GroupType, name: str, permissions: List[str]) -> None :
    """Assert the group has the single specified permission."""
    group: Group = Group.objects.get(label = self.label, name = name)
    self.assertEqual(group_type, group.group_type)
    self.assertEqual(1 + len(permissions), len(group.permissions.all()))
    self.assertEqual(self.permission_object, group.permissions.all()[len(permissions)])
    for index, permission in enumerate(permissions):
      self.assertEqual(permission, group.permissions.all()[len(permissions) - index - 1].codename)


  def create_permission(self, *, name: str) -> Permission :
    """Create permissions as test data."""
    # noinspection PyUnresolvedReferences
    return Permission.objects.create(codename = name, name = name, content_type = self.content_type)  # type: ignore[misc]
