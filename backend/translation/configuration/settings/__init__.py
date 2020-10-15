"""Return the correct settings."""

# khaleesi.ninja
from base.settings.server import get_server_type


# pylint: disable=exec-used
exec('from .{type} import *'.format(type = get_server_type()))
