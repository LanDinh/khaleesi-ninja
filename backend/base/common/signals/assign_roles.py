"""Connect custom signals."""

# Python.
from typing import Any

# Django.
from django.db.models.signals import post_save
from django.dispatch import receiver

# khaleesi.ninja.
from common.models import User, Role, RoleAssignment


@receiver(post_save, sender = User, dispatch_uid = 'common.signals.assign_roles.creating_user')
def assign_roles_when_creating_user(instance: User, created: bool, **_: Any) -> None :
  """Make sure that all users get assigned the authenticated roles."""
  if created and instance.is_authenticated:
    for role in Role.objects.authenticated():
      RoleAssignment.objects.get_or_create(user = instance, role = role)


@receiver(post_save, sender = Role)
def assign_roles_when_saving_role(instance: Role, **_: Any) -> None :
  """Make sure that if a role gets saved, the role assignments get adjusted."""
  if instance.authenticated:
    for user in User.objects.without_role_assignment(role = instance):
      RoleAssignment.objects.get_or_create(user = user, role = instance)
  else:
    instance.users.clear()
