"""Test the core-clocktower bellringer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import ObjectMetadata, ObjectMetadataRequest, JobExecutionRequest
from khaleesi.proto.core_clocktower_pb2 import JobRequest, Job
from microservice.service.bellringer import Service

@patch('microservice.service.bellringer.LOGGER')
class BellRingerServiceTestCase(SimpleTestCase):
  """Test the core-clocktower bellringer service."""

  service = Service()

  @patch('microservice.service.bellringer.Job.objects.khaleesiCreate')
  def testCreateJob(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    create.return_value.toObjectMetadata.return_value = ObjectMetadata()
    create.return_value.toGrpc.return_value = Job()
    # Execute test.
    self.service.CreateJob(JobRequest(), MagicMock())
    # Assert result.
    create.assert_called_once()

  @patch('microservice.service.bellringer.Job.objects.get')
  @patch('microservice.service.bellringer.ACTUATOR')
  def testExecuteJob(self, actuator: MagicMock, job: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    job.return_value.toGrpcJobExecutionRequest.return_value = '', JobExecutionRequest()
    # Execute test.
    self.service.ExecuteJob(ObjectMetadataRequest(), MagicMock())
    # Assert result.
    job.return_value.toGrpcJobExecutionRequest.assert_called_once()
    actuator.actuate.assert_called_once()
