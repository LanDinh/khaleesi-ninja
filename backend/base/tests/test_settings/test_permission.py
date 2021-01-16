"""Test base permission."""

# Python.
from typing import Optional
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from django.http import HttpRequest
from rest_framework.request import Request

from common.exceptions import PermissionDeniedException, TeapotException
from common.models import User, Role, RoleAssignment
from common.models.auth.feature.feature_state import FeatureState
from common.service_type import ServiceType
from common.views import View
from settings.permission import Permission
from settings.settings import UserNames
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


# noinspection PyUnresolvedReferences,PyTypeHints,PyMissingOrEmptyDocstring,PyTypeChecker
class PermissionUnitTests(TestUserUnitMixin, SimpleTestCase):
  """Test base permission."""

  permission = Permission()

  @patch.object(User.objects, 'get')
  def test_anonymous_has_permission(self, user_get: MagicMock) -> None :
    """Test if permission is checked correctly."""
    # Prepare data.
    request = MagicMock()
    request.user = self.setup_anon(user_get = user_get, permission = True)
    # Perform test.
    result = self.permission.has_permission(request, self.setup_view())
    # Assert result.
    self.assertTrue(result)

  @patch.object(User.objects, 'get')
  def test_anonymous_has_no_permission(self, user_get: MagicMock) -> None :
    """Test if permission is checked correctly."""
    # Prepare data.
    request = MagicMock()
    request.user = self.setup_anon(user_get = user_get, permission = False)
    # Perform test.
    with self.assertRaises(PermissionDeniedException):
      self.permission.has_permission(request, self.setup_view())

  @patch.object(User.objects, 'get')
  def test_user_has_permission(self, user_get: MagicMock) -> None :
    """Test if permission is checked correctly."""
    # Prepare data.
    self.setup_anon(user_get = user_get)
    for params in self.params():
      with self.subTest(params = params):
        user = self.create_user(params = params)
        user.has_permission = MagicMock(return_value = True)  # type: ignore[assignment]
        request = MagicMock()
        request.user = user
        # Perform test.
        result = self.permission.has_permission(request, self.setup_view())
        # Assert result.
        self.assertTrue(result)

  @patch.object(User.objects, 'get')
  def test_user_has_no_permission(self, user_get: MagicMock) -> None :
    """Test if permission is checked correctly."""
    # Prepare data.
    self.setup_anon(user_get = user_get)
    for params in self.params():
      with self.subTest(params = params):
        user = self.create_user(params = params)
        user.has_permission = MagicMock(return_value = False)  # type: ignore[assignment]
        request = MagicMock()
        request.user = user
        # Perform test.
        with self.assertRaises(PermissionDeniedException):
          self.permission.has_permission(request, self.setup_view())

  def test_forbidden_views(self) -> None :
    """Test if permission is checked correctly."""
    with self.assertRaises(TeapotException):
      self.permission.has_permission(request = {}, view = {})  # type: ignore[arg-type]

  def setup_anon(self, *, user_get: MagicMock, permission: Optional[bool] = None) -> User :
    """Setup the anonymous user."""
    anon =  self.create_anonymous_user()
    anon.has_permission = MagicMock(return_value = permission)  # type: ignore[assignment]
    user_get.return_value = anon
    return anon

  @staticmethod
  def setup_view() -> MagicMock :
    """Setup the view."""
    view = MagicMock()
    view.service = ServiceType.TRANSLATE
    view.feature = 'test'
    return view


class TestView(View):
  """Test view for tests."""

  service: ServiceType = ServiceType.TRANSLATE
  feature: str = ''

  def __init__(self, service: ServiceType, feature: str) -> None :
    """Instantiate test view."""
    super().__init__()
    self.service = service
    self.feature = feature


# noinspection PyUnresolvedReferences,PyTypeChecker,PyMissingOrEmptyDocstring
class PermissionIntegrationTests(TestUserIntegrationMixin, TestCase):
  """Test base permission."""

  permission = Permission()
  feature_name = 'test'

  def test_anonymous_has_permission(self) -> None :
    """Test if permission is checked correctly."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        user = User.objects.get(username = UserNames.anonymous())
        self.grant_permission(user = user, service = service)
        view = TestView(service = service, feature = self.feature_name)
        request = Request(request = HttpRequest())
        request.user = user
        # Perform test.
        result = self.permission.has_permission(request = request, view = view)
        # Assert result.
        self.assertTrue(result)
        self.cleanup_user_roles(user = user)

  def test_anonymous_has_no_permission(self) -> None :
    """Test if permission is checked correctly."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        user = User.objects.get(username = UserNames.anonymous())
        view = TestView(service = service, feature = self.feature_name)
        request = Request(request = HttpRequest())
        request.user = user
        # Perform test.
        with self.assertRaises(PermissionDeniedException):
          self.permission.has_permission(request = request, view = view)
        self.cleanup_user_roles(user = user)

  def test_active_user_has_permission(self) -> None :
    """Test if permission is checked correctly."""
    for params in self.params_active_only():
      user = self.create_user(params = params)
      for service in ServiceType:
        with self.subTest(user = params, service = service):
          # Prepare data.
          self.grant_permission(user = user, service = service)
          view = TestView(service = service, feature = self.feature_name)
          request = Request(request = HttpRequest())
          request.user = user
          # Perform test.
          result = self.permission.has_permission(request = request, view = view)
          # Assert result.
          self.assertTrue(result)
          self.cleanup_user_roles(user = user)
      user.delete()

  def test_active_user_has_no_permission(self) -> None :
    """Test if permission is checked correctly."""
    for params in self.params():
      user = self.create_user(params = params)
      for service in ServiceType:
        with self.subTest(user = params, service = service):
          # Prepare data.
          view = TestView(service = service, feature = self.feature_name)
          request = Request(request = HttpRequest())
          request.user = user
          # Perform test.
          with self.assertRaises(PermissionDeniedException):
            self.permission.has_permission(request = request, view = view)
          self.cleanup_user_roles(user = user)
      user.delete()

  def test_inactive_user_has_no_permission(self) -> None :
    """Test if permission is checked correctly."""
    for params in self.params_inactive_only():
      user = self.create_user(params = params)
      for service in ServiceType:
        with self.subTest(user = params, service = service):
          # Prepare data.
          self.grant_permission(user = user, service = service)
          view = TestView(service = service, feature = self.feature_name)
          request = Request(request = HttpRequest())
          request.user = user
          # Perform test.
          with self.assertRaises(PermissionDeniedException):
            self.permission.has_permission(request = request, view = view)
          self.cleanup_user_roles(user = user)
      user.delete()

  def test_forbidden_views(self) -> None :
    """Test if permission is checked correctly."""
    with self.assertRaises(TeapotException):
      self.permission.has_permission(request = {}, view = {})  # type: ignore[arg-type]

  def grant_permission(self, *, user: User, service: ServiceType) -> None :
    """Grant permission to the user."""
    Role.migrations.create(service = service, name = self.feature_name)
    role = Role.objects.get(service = service.name, name = self.feature_name)
    RoleAssignment.objects.get_or_create(user = user, role = role)
    feature, _ = role.features.get_or_create(service = service, name = self.feature_name)
    feature.state = FeatureState.RELEASED.name
    feature.save()

  @staticmethod
  def cleanup_user_roles(*, user: User) -> None :
    """Delete all roles and associated features."""
    for role_assignment in user.roleassignment_set.all():
      role = role_assignment.role
      for feature in role.features.all():
        feature.delete()
      role_assignment.delete()
      role.delete()
