"""The common config."""

# khaleesi.ninja.
from common.app_config import AppConfig, KhaleesiMeta


class CommonConfig(AppConfig):
  """The common config."""
  name = 'common'
  khaleesi_meta = KhaleesiMeta(
      label = 'base_common',
      anonymous_group_permissions = ['user.views.csrf'],
      authenticated_group_permissions = ['user.views.csrf'],
      groups = [],
  )
