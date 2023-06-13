"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import IdRequest, JobRequest as BaseJobRequest
from khaleesi.proto.core_clocktower_pb2 import JobRequest
from microservice.service.bellringer import Service

@patch('microservice.service.bellringer.LOGGER')
class BellRingerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch('microservice.service.bellringer.Job.objects.create_job')
  def test_create_job(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    request = JobRequest()
    create.return_value.job_id = 'job-id'
    # Execute test.
    result = self.service.CreateJob(request, MagicMock())
    # Assert result.
    create.assert_called_once_with(grpc_job = request.job)
    self.assertEqual(create.return_value.job_id, result.id)

  @patch('microservice.service.bellringer.Job.objects.get_job_request')
  @patch('microservice.service.bellringer.ACTUATOR')
  def test_execute_job(self, actuator: MagicMock, job_request: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    request = IdRequest()
    job_request.return_value = '', BaseJobRequest()
    # Execute test.
    self.service.ExecuteJob(request, MagicMock())
    # Assert result.
    job_request.assert_called_once()
    actuator.actuate.assert_called_once()
