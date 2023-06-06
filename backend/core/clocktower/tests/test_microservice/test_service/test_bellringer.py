"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import IdMessage
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob
from microservice.service.bellringer import Service

@patch('microservice.service.bellringer.LOGGER')
class BellRingerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch('microservice.service.bellringer.Job.objects.create_job')
  def test_create_job(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    request = GrpcJob()
    create.return_value.job_id = 'job-id'
    # Execute test.
    result = self.service.CreateJob(request, MagicMock())
    # Assert result.
    create.assert_called_once_with(grpc_job = request)
    self.assertEqual(create.return_value.job_id, result.id)

  @patch('microservice.service.bellringer.ACTUATOR')
  def test_execute_job(self, actuator: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    request = IdMessage()
    # Execute test.
    self.service.ExecuteJob(request, MagicMock())
    # Assert result.
    actuator.actuate.assert_called_once()