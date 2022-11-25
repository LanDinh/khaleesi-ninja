"""Provide a mock for testing."""

# khaleesi.ninja.
from khaleesi.core.shared.state import State, Request


TEST_STATE = State(
  request = Request(id = 13, service_name = 'service', method_name  = 'method'),
)
