"""Custom User model."""

# Python.
from __future__ import annotations
from datetime import datetime

# Django.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.postgres.fields import CICharField
from django.db import models
from django.utils import timezone

# khaleesi.ninja.
from settings.settings import Settings, UserNames
from common.models.user.manager_default import DefaultManager
from common.models.user.manager_migrations import MigrationManager
from common.models.model import Model

class User(Model, AbstractBaseUser, PermissionsMixin):
  """Custom User."""
  # The username. Enforcement: non-blank, unique, length, case insensitive.
  # Allowed characters: unicode plus # @.+-_
  username = CICharField(
      max_length = 150,
      blank = True,  # The blank username is reserved for the anonymous user.
      unique = True,
      validators = [UnicodeUsernameValidator()],
  )
  # Lock a certain username to avoid impersonation by pointing to the real user.
  original = models.ForeignKey(
      'self',
      on_delete = models.CASCADE,
      null = True,
      blank = True,
      related_name = 'alias',
  )

  # Admin lock an account.
  admin_locked = models.BooleanField(default = False)
  # Automatically lock an account for a some time upon too many failed logins.
  failed_attempts = models.PositiveSmallIntegerField(default = 0)
  # The timestamp of when the last system lock was added.
  system_locked = models.DateTimeField(default = datetime.min)

  # The timestamp of when the account was created.
  date_joined = models.DateTimeField(default = timezone.now)
  # The date of the last request that had this user attached.
  last_activity = models.DateTimeField(default = timezone.now)

  @property
  def is_active(self) -> bool :
    """Locked users should count as inactive."""
    return not self.is_admin_locked() and not self.is_system_locked()

  # noinspection PyTypeHints,SyntaxError
  @property
  def is_authenticated(self) -> bool :  # type: ignore[override]
    """Check if the user is authenticated."""
    return not self.username is UserNames.anonymous()

  USERNAME_FIELD = 'username'  # pylint: disable=invalid-name

  objects = DefaultManager()
  migrations = MigrationManager()

  def is_alias(self) -> bool :
    """Return the alias state of the User."""
    if self.original:
      return True
    return False

  def is_oauth_only(self) -> bool :
    """Return the oauth state of the User."""
    return not self.has_usable_password()

  def is_admin_locked(self) -> bool :
    """Return the admin lock state of the User."""
    return self.admin_locked

  def is_system_locked(self) -> bool :
    """Return the system lock state of the User."""
    system_lock_time = Settings.system_lock_time()
    return timezone.now() < self.system_locked + system_lock_time
