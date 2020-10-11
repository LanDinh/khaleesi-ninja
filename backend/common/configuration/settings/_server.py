"""Determine which platform the server is running on."""

# Python.
import socket


def get_server_type() -> str :
  """Determine the platform by checking the hostname."""
  server = socket.gethostname()
  if server == 'khaleesi-ninja':
    return 'production'
  if server == 'khaleesi-testing':
    return 'testing'
  return 'development'
