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

  @patch('microservice.actuator.actuator.DbJobExecution.objects.khaleesiCreate')
  def testActuateUnknownAction(self, jobExecution: MagicMock) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    with self.assertRaises(InvalidArgumentException) as exception:
      # Execute test.
      ACTUATOR.actuate(action = 'unknown.action.name', request = JobExecutionRequest())
      # Assert result.
      self.assertIn('exists', exception.exception.privateMessage)
      jobExecution.return_value.toObjectMetadata.assert_called_once()
      jobExecution.return_value.khaleesiSave.assert_called_once()

  @patch('microservice.actuator.actuator.DbJobExecution.objects.khaleesiCreate')
  def testActuate(self, jobExecution: MagicMock) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    # Prepare data.
    mock = MagicMock()
    request = JobExecutionRequest()
    request.jobExecution.executionMetadata.id = 'execution-id'
    # Execute test.
    with patch.dict('microservice.actuator.actuator.CORE', { 'some': { 'action': mock } }):
      ACTUATOR.actuate(action = 'core.some.action', request = request)
    # Assert result.
    mock.assert_called_once()
    jobExecution.return_value.toObjectMetadata.assert_called_once()
