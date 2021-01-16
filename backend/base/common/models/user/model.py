"""Custom User model."""

# Python.
from __future__ import annotations

# Django.
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.postgres.fields import CICharField
from django.db import models

# khaleesi.ninja.
from common.models.auth.feature.model import Feature
from common.models.auth.feature.feature_state import FeatureState
from common.models.auth.role.model import Role
from common.models.user.manager_default import DefaultManager
from common.models.user.manager_migrations import MigrationManager
from common.models.model import Model
from common.service_type import ServiceType
from settings.settings import Settings, UserNames


class User(Model, AbstractBaseUser):
  """Custom User."""
  # The username. Enforcement: non-blank, unique, length, case insensitive.
  # Allowed characters: unicode plus # @.+-_
  username = CICharField(
      max_length = 150,
      blank = True,  # The blank username is reserved for the anonymous user.
      unique = True,
      validators = [UnicodeUsernameValidator()],
  )

  # Roles granting access to services and features.
  roles = models.ManyToManyField(Role, through = 'RoleAssignment', related_name = 'users')

  # Mark an account as deleted.
  deleted = models.BooleanField(default = False)
  # Admin lock an account.
  admin_locked = models.BooleanField(default = False)
  # Automatically lock an account after too many failed logins.
  failed_attempts = models.PositiveSmallIntegerField(default = 0)

  # The timestamp of when the account was created.
  date_joined = models.DateTimeField(auto_now_add = True)

  USERNAME_FIELD = 'username'  # pylint: disable=invalid-name

  objects: DefaultManager[User] = DefaultManager()
  migrations: MigrationManager[User] = MigrationManager()

  # noinspection PyTypeHints,SyntaxError
  @property
  def is_authenticated(self) -> bool :  # type: ignore[override]
    """Check if the user is authenticated."""
    return not self.username is UserNames.anonymous()

  @property
  def is_active(self) -> bool :
    """Locked users should count as inactive."""
    return not self.deleted and not self.admin_locked and not self.system_locked

  @property
  def system_locked(self) -> bool :
    """Check if the user is system locked."""
    return self.failed_attempts > Settings.max_failed_attempts()

  def has_permission(self, service: ServiceType, name: str) -> bool :
    """Check if a user has access to a certain feature."""
    if not self.is_active:
      return False
    feature, _ = Feature.objects.get_or_create(service = service, name = name)
    role_assignments = self.roleassignment_set.get_queryset().filter(  # pylint: disable=no-member
        role__features = feature
    )
    for role in role_assignments:
      if feature.state == FeatureState.BETA.name and role.beta:
        return True
      if feature.state == FeatureState.RELEASED.name:
        return True
    return False
