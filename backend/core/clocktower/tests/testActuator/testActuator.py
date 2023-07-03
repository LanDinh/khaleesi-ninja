"""Test the actuator."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecutionRequest
from microservice.actuator.actuator import ACTUATOR


class ActuatorTest(SimpleTestCase):
  """Test the actuator."""

  def testActuateWrongActionNameFormat(self) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    with self.assertRaises(InvalidArgumentException) as exception:
      # Execute test.
      ACTUATOR.actuate(action = 'invalid-name', request = JobExecutionRequest())
      # Assert result.
      self.assertIn('wrong format', exception.exception.privateMessage)

  def testActuateUnknownAction(self) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    with self.assertRaises(InvalidArgumentException) as exception:
      # Execute test.
      ACTUATOR.actuate(action = 'unknown.action.name', request = JobExecutionRequest())
      # Assert result.
      self.assertIn('exists', exception.exception.privateMessage)

  def testActuate(self) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    # Prepare data.
    mock = MagicMock()
    request = JobExecutionRequest()
    request.jobExecution.executionMetadata.id = 'execution-id'
    # Execute test.
    with patch.dict('microservice.actuator.actuator.CORE', { 'some': { 'action': mock } }):
      result = ACTUATOR.actuate(action = 'core.some.action', request = request)
    # Assert result.
    mock.assert_called_once()
    self.assertEqual(request.jobExecution.executionMetadata, result)
