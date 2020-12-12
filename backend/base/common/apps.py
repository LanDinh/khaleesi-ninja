"""The common config."""

# Django.
from django.db.models.signals import post_migrate

# khaleesi.ninja.
from common.app_config import AppConfig


class CommonConfig(AppConfig):
  """The common config."""
  service_name = 'base'
  name = 'common'

  # noinspection PyUnresolvedReferences
  def ready(self) -> None :
    """Handle signals."""
    # Disconnect unwanted signals.
    post_migrate.disconnect(
        dispatch_uid = 'django.contrib.auth.management.create_permissions',
    )
    # Connect custom signals.
    # pylint: disable=unused-import,import-outside-toplevel
    from common import signals
