"""Provide a mock for testing."""

# khaleesi.ninja.
from khaleesi.core.shared.state import State


class TestState(State):
  """Set default values suitable for tests."""

  def reset(self) -> None :
    """Set default values suitable for tests."""
    super().reset()
    self.request.id           = 13
    self.request.service_name = 'service'
    self.request.method_name  = 'method'
TEST_STATE = TestState()
