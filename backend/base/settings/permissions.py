"""Custom permissions for khaleesi.ninja."""

# Django.
from django.views import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

# khaleesi.ninja.
from common.exceptions import PermissionDeniedException
from common.models import User
from settings.settings import UserNames


class HasPermission(BasePermission):
  """Grant permission if the User has the correct permissions."""

  def has_permission(self, request: Request, view: View) -> bool :
    """Return if the user has permission to access this view."""
    if not request.user.is_authenticated:
      request.user = User.objects.get(username = UserNames.anonymous())
    if not request.user.has_perm(view.permission):  # type: ignore[attr-defined]
      raise PermissionDeniedException()
    return True
