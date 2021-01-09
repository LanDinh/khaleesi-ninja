"""Make sure that users can only access views they have permission to."""

# pylint: disable=line-too-long

# Django.
from django.views.generic.base import View
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

# khaleesi.ninja.
from common.exceptions import PermissionDeniedException, TeapotException
from common.models import User
from settings.settings import UserNames


class Permission(BasePermission):
  """Make sure that users can only access views they have permission to."""

  def has_permission(self, request: Request, view: View) -> bool :
    """Base permission for views."""
    if not hasattr(view, 'service') or not hasattr(view, 'feature'):
      raise TeapotException(data = 'Forbidden view!')
    user = User.objects.get(username = UserNames.anonymous())
    if request.user.is_authenticated:
      user = request.user

    if not user.has_permission(service = view.service, name = view.feature):  # type: ignore[attr-defined]
      raise PermissionDeniedException()

    return True
