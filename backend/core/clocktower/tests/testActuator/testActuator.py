"""Test the actuator."""

# Python.
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import InvalidArgumentException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import JobExecution
from microservice.actuator.actuator import ACTUATOR


class ActuatorTest(SimpleTestCase):
  """Test the actuator."""

  @patch('microservice.actuator.actuator.addRequestMetadata')
  @patch('microservice.actuator.actuator.DbJobExecution.objects.khaleesiCreate')
  @patch('microservice.actuator.actuator.Job.objects.get')
  def testActuateUnknownAction(
      self,
      job            : MagicMock,
      execution      : MagicMock,
      requestMetadata: MagicMock,
  ) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    with self.assertRaises(InvalidArgumentException) as exception:
      # Prepare data.
      grpc = JobExecution()
      grpc.action.site   = 'unknown'
      grpc.action.app    = 'unknown'
      grpc.action.action = 'unknown'
      job.return_value.toGrpcJobExecutionRequest.return_value = grpc
      # Execute test.
      ACTUATOR.actuate(jobId = 'job-id')
      # Assert result.
      requestMetadata.assert_called_once()
      self.assertIn('exists', exception.exception.privateMessage)
      execution.return_value.toObjectMetadata.assert_called_once()
      execution.return_value.khaleesiSave.assert_called_once()

  @patch('microservice.actuator.actuator.addRequestMetadata')
  @patch('microservice.actuator.actuator.DbJobExecution.objects.khaleesiCreate')
  @patch('microservice.actuator.actuator.Job.objects.get')
  def testActuate(self, job: MagicMock, execution: MagicMock, requestMetadata: MagicMock) -> None :
    """Actuating a job should fail if the action name has the wrong format."""
    # Prepare data.
    grpc = JobExecution()
    grpc.action.site   = 'core'
    grpc.action.app    = 'app'
    grpc.action.action = 'action'
    job.return_value.toGrpcJobExecutionRequest.return_value = grpc
    mock = MagicMock()
    execution.return_value.toGrpc.return_value = grpc
    # Execute test.
    with patch.dict('microservice.actuator.actuator.CORE', { 'app': { 'action': mock } }):
      ACTUATOR.actuate(jobId = 'job-id')
    # Assert result.
    requestMetadata.assert_called_once()
    mock.assert_called_once()
    execution.return_value.toObjectMetadata.assert_called_once()
