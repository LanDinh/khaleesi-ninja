"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import IdRequest, JobRequest as BaseJobRequest
from khaleesi.proto.core_clocktower_pb2 import JobRequest
from microservice.service.bellringer import Service

@patch('microservice.service.bellringer.LOGGER')
class BellRingerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch('microservice.service.bellringer.Job.objects.createJob')
  def testCreateJob(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    request = JobRequest()
    create.return_value.jobId = 'job-id'
    # Execute test.
    result = self.service.CreateJob(request, MagicMock())
    # Assert result.
    create.assert_called_once_with(grpcJob = request.job)
    self.assertEqual(create.return_value.jobId, result.id)

  @patch('microservice.service.bellringer.Job.objects.getJobRequest')
  @patch('microservice.service.bellringer.ACTUATOR')
  def testExecuteJob(self, actuator: MagicMock, jobRequest: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    request = IdRequest()
    jobRequest.return_value = '', BaseJobRequest()
    # Execute test.
    self.service.ExecuteJob(request, MagicMock())
    # Assert result.
    jobRequest.assert_called_once()
    actuator.actuate.assert_called_once()
