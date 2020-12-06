"""Test the custom permissions."""

# pylint: disable=line-too-long

# Python.
from dataclasses import asdict, dataclass
from typing import Tuple
from unittest.mock import MagicMock, patch

# Django.
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# khaleesi.ninja.
from common.exceptions import PermissionDeniedException
from common.models import User
from settings.permissions import HasPermission
from settings.settings import Settings
from test_util.models.user import TestUserIntegrationMixin, TestUserUnitMixin, Parameters
from test_util.test import SimpleTestCase, TestCase


class PermissionUnitTests(TestUserUnitMixin, SimpleTestCase):
  """Unit tests for the custom permissions."""

  permission = HasPermission()
  permission_name = 'test.test'

  def test_permission_denied(self) -> None :
    """Test if PermissionDenied is raised correctly."""
    for username in ['username', Settings.anonymous_username()]:
      for params in self.params():
        with self.subTest(username = username, **asdict(params)):
          # Prepare data.
          params.creates.username = username
          request, view, user, expected = self.create_mocks(params = params)
          # noinspection PyTypeHints
          user.has_perm.return_value = False
          with self.assertRaises(PermissionDeniedException):
            # Perform test.
            self.permission.has_permission(request = request, view = view)
          # Assert result.
          user.has_perm.assert_called_once_with(self.permission_name)
          user.save.assert_not_called()
          self.assert_user(user = user, expected_user = expected)

  @patch.object(User.objects, 'get_anonymous_user')
  def test_permission_granted_authenticated(self, anonymous: MagicMock) -> None :
    """Test if permission is granted correctly."""
    for params in self.params():
      with self.subTest(**asdict(params)):
        # Prepare data.
        request, view, user, expected_user = self.create_mocks(params = params)
        # noinspection PyTypeHints
        user.has_perm.return_value = True
        # Perform test.
        check = self.permission.has_permission(request = request, view = view)
        # Assert result.
        self.assertTrue(check)
        anonymous.assert_not_called()
        user.has_perm.assert_called_once_with(self.permission_name)
        user.save.assert_not_called()
        self.assert_user(user = user, expected_user = expected_user)

  @patch.object(User.objects, 'get_anonymous_user')
  def test_permission_granted_anonymous(
      self,
      anonymous: MagicMock,
  ) -> None :
    """Test if permission is granted correctly."""
    for params in self.params():
      with self.subTest(**asdict(params)):
        # Prepare data.
        params.creates.username = Settings.anonymous_username()
        request, view, user, expected_user = self.create_mocks(params = params)
        user.is_authenticated = False
        expected_user.is_authenticated = False
        anonymous.return_value = user
        user.has_perm.return_value = True
        # Perform test.
        check = self.permission.has_permission(request = request, view = view)
        # Assert result.
        self.assertTrue(check)
        user.has_perm.assert_called_once_with(self.permission_name)
        user.save.assert_not_called()
        self.assert_user(user = user, expected_user = expected_user)
        anonymous.assert_called_once_with()
        anonymous.reset_mock()

  def create_mocks(
      self, *,
      params: Parameters,
  ) -> Tuple[MagicMock, MagicMock, MagicMock, MagicMock] :
    """Create all necessary mocks."""
    request = MagicMock()
    view = MagicMock()
    view.permission = self.permission_name
    user, expected_user = self.create_mock_user(params = params)
    request.user = user
    return request, view, user, expected_user


@dataclass
class Request:
  """Request for use in testing."""
  user: User

@dataclass
class View:
  """View for use in testing."""
  permission: str


class PermissionIntegrationTests(TestUserIntegrationMixin, TestCase):
  """Integration tests for the custom permissions."""

  permission = HasPermission()
  label = 'test'
  granted_name = 'granted'
  denied_name = 'denied'
  granted: Permission
  denied: Permission
  denied_fullname = f'{label}.{denied_name}'
  granted_fullname = f'{label}.{granted_name}'

  @classmethod
  def setUpClass(cls) -> None :
    """Prepare permissions for testing."""
    super().setUpClass()
    content_type, _ = ContentType.objects.get_or_create(
        model = Settings.permission_model(),
        app_label = cls.label,
    )
    cls.granted = Permission.objects.create(
        codename = cls.granted_name,
        name = cls.granted_name,
        content_type = content_type,
    )
    cls.denied = Permission.objects.create(
        codename = cls.denied_name,
        name = cls.denied_name,
        content_type = content_type,
    )
    User.migrations.get_or_create_anonymous_user()
    # noinspection PyUnresolvedReferences
    User.objects.get_anonymous_user().user_permissions.add(cls.granted)  # type: ignore[attr-defined]

  @classmethod
  def tearDownClass(cls) -> None :
    """Clean up test permissions."""
    cls.granted.delete()
    cls.denied.delete()

  def test_anonymous_permission_denied(self) -> None :
    """Test if PermissionDenied is raised correctly."""
    # Prepare data.
    # noinspection PyTypeChecker
    request = Request(user = User.objects.get_anonymous_user())
    view = View(self.denied_fullname)
    with self.assertRaises(PermissionDeniedException):
      # Perform test.
      # noinspection PyUnresolvedReferences
      self.permission.has_permission(request = request, view = view)  # type: ignore[arg-type]

  def test_anonymous_permission_granted(self) -> None :
    """Test if permission is granted correctly."""
    # Prepare data.
    # noinspection PyTypeChecker
    request = Request(user = User.objects.get_anonymous_user())
    view = View(self.granted_fullname)
    # Perform test.
    # noinspection PyUnresolvedReferences
    check = self.permission.has_permission(request = request, view = view)  # type: ignore[arg-type]
    # Assert result.
    self.assertTrue(check)

  def test_authenticated_permission_denied(self) -> None :
    """Test if PermissionDenied is raised correctly."""
    for params in self.params_no_active_superuser():
      with self.subTest(**asdict(params)):
        # Prepare data.
        user, expected_user = self.create_user(params = params)
        user.user_permissions.add(self.granted)
        request = Request(user = user)
        view = View(self.denied_fullname)
        with self.assertRaises(PermissionDeniedException):
          # Perform test.
          # noinspection PyUnresolvedReferences
          self.permission.has_permission(request = request, view = view)  # type: ignore[arg-type]
        # Assert result.
        self.assert_user(expected_user = expected_user)


  def test_authenticated_permission_granted(self) -> None :
    """Test if permission is granted correctly."""
    for params in self.params_only_active_users():
      with self.subTest(**asdict(params)):
        # Prepare data.
        user, expected_user = self.create_user(params = params)
        user.user_permissions.add(self.granted)
        request = Request(user = user)
        view = View(self.granted_fullname)
        # Perform test.
        # noinspection PyUnresolvedReferences
        check = self.permission.has_permission(request = request, view = view)  # type: ignore[arg-type]
        # Assert result.
        self.assertTrue(check)
        self.assert_user(expected_user = expected_user)
