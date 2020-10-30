"""The common config."""

# Django.
from django.db.models.signals import post_migrate

# khaleesi.ninja.
from settings.app_config import AppConfig, KhaleesiMeta


class CommonConfig(AppConfig):
  """The common config."""
  name = 'common'
  khaleesi_meta = KhaleesiMeta(
      label = 'base_common',
      anonymous_group_permissions = ['user.views.csrf'],
      authenticated_group_permissions = ['user.views.csrf'],
      groups = [],
  )

  # noinspection PyUnresolvedReferences
  def ready(self) -> None :
    """Handle signals."""
    # Disconnect unwanted signals.
    post_migrate.disconnect(
        dispatch_uid = 'django.contrib.auth.management.create_permissions',
    )
    # Connect custom signals.
    # pylint: disable=import-outside-toplevel,unused-import
    from settings import signals
