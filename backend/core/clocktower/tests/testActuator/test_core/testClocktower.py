"""Test core-clocktower batch jobs."""

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import Action
from microservice.actuator.core.clocktower import (
  addAppForUpdateJobExecutionStateGenerator,
  CLOCKTOWER,
)


class ClocktowerJobTestCase(SimpleTestCase):
  """Test core-sawmill batch jobs."""

  def testAddAppForUpdateJobExecutionStateGenerator(self) -> None :
    """Test cleaning up requests."""
    # Prepare data.
    action = Action()
    action.site = 'site'
    action.app  = 'app'
    # Execute test.
    addAppForUpdateJobExecutionStateGenerator(action = action)
    # Assert result.
    self.assertIn('update-job-execution-state-site-app', CLOCKTOWER)
