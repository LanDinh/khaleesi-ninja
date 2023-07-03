"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata, JobExecutionRequest
from khaleesi.proto.core_clocktower_pb2 import JobRequest
from microservice.service.bellringer import Service

@patch('microservice.service.bellringer.LOGGER')
class BellRingerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch('microservice.service.bellringer.Job.objects.khaleesiCreate')
  def testCreateJob(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Execute test.
    self.service.CreateJob(JobRequest(), MagicMock())
    # Assert result.
    create.assert_called_once()
    create.return_value.toGrpc.assert_called_once()

  @patch('microservice.service.bellringer.Job.objects.khaleesiGet')
  @patch('microservice.service.bellringer.ACTUATOR')
  def testExecuteJob(self, actuator: MagicMock, job: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    job.return_value.toGrpcJobExecutionRequest.return_value = '', JobExecutionRequest()
    # Execute test.
    self.service.ExecuteJob(ObjectMetadata(), MagicMock())
    # Assert result.
    job.return_value.toGrpcJobExecutionRequest.assert_called_once()
    actuator.actuate.assert_called_once()
