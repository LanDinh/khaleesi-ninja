"""Return the correct settings."""

# khaleesi.ninja
from base_settings.server import get_server_type


# pylint: disable=exec-used
exec(f'from .{get_server_type()} import *')
