"""Test the job."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob
from microservice.models import Job


class JobTestCase(SimpleTestCase):
  """Test the job model."""

  @patch('microservice.models.job.JobConfigurationMixin.jobConfigurationToGrpc')
  def testToGrpcJobExecutionRequest(self, jobConfiguration: MagicMock) -> None :
    """Test getting a gRPC job execution request."""
    # Prepare data.
    job = Job(khaleesiId = 'job-id')
    # Execute test.
    result = job.toGrpcJobExecutionRequest()
    # Assert result.
    jobConfiguration.assert_called_once()
    self.assertEqual(job.khaleesiId, result.jobMetadata.id)

  @patch('microservice.models.job.JobConfigurationMixin.jobConfigurationFromGrpc')
  @patch('microservice.models.job.Model.khaleesiSave')
  def testKhaleesiSave(self, parent: MagicMock, jobConfiguration: MagicMock) -> None :
    """Test setting the values from gRPC."""
    # Prepare data.
    job = Job()
    grpc = GrpcJob()
    grpc.name           = 'name'
    grpc.description    = 'description'
    grpc.cronExpression = 'cronExpression'
    # Execute test.
    job.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    jobConfiguration.assert_called_once()
    self.assertEqual(grpc.name          , job.name)
    self.assertEqual(grpc.description   , job.description)
    self.assertEqual(grpc.cronExpression, job.cronExpression)

  @patch('microservice.models.job.JobConfigurationMixin.jobConfigurationToGrpc')
  def testToGrpc(self, jobConfiguration: MagicMock) -> None :
    """Test returning a gRPC."""
    # Prepare data.
    job = Job(
      name           = 'name',
      description    = 'description',
      cronExpression = 'cron',
    )
    # Execute test.
    result = job.toGrpc()
    # Assert result.
    jobConfiguration.assert_called_once()
    self.assertEqual(job.name          , result.name)
    self.assertEqual(job.description   , result.description)
    self.assertEqual(job.cronExpression, result.cronExpression)
