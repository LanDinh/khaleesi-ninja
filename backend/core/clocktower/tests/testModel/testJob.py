"""Test the job."""

# Python.
from unittest.mock import patch, MagicMock
from uuid import UUID

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob
from microservice.models import Job


class JobTestCase(SimpleTestCase):
  """Test the job model."""

  @patch('microservice.models.job.JobConfigurationMixin.jobConfigurationToGrpc')
  @patch('microservice.models.job.addRequestMetadata')
  def testToGrpcJobExecutionRequest(
      self,
      requestMetadata : MagicMock,
      jobConfiguration: MagicMock,
  ) -> None :
    """Test getting a gRPC job execution request."""
    # Prepare data.
    job = Job(khaleesiId = 'job-id', action = 'action')
    # Execute test.
    action, result = job.toGrpcJobExecutionRequest()
    # Assert result.
    requestMetadata.assert_called_once()
    jobConfiguration.assert_called_once()
    self.assertEqual(job.khaleesiId, result.jobExecution.jobMetadata.id)
    self.assertTrue(UUID(result.jobExecution.executionMetadata.id))
    self.assertEqual(job.action, action)

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
    grpc.action         = 'action'
    # Execute test.
    job.khaleesiSave(grpc = grpc)
    # Assert result.
    parent.assert_called_once()
    jobConfiguration.assert_called_once()
    self.assertEqual(grpc.name          , job.name)
    self.assertEqual(grpc.description   , job.description)
    self.assertEqual(grpc.cronExpression, job.cronExpression)
    self.assertEqual(grpc.action        , job.action)

  @patch('microservice.models.job.JobConfigurationMixin.jobConfigurationToGrpc')
  def testToGrpc(self, jobConfiguration: MagicMock) -> None :
    """Test returning a gRPC."""
    # Prepare data.
    job = Job(
      name           = 'name',
      description    = 'description',
      cronExpression = 'cron',
      action         = 'action',
    )
    # Execute test.
    result = job.toGrpc()
    # Assert result.
    jobConfiguration.assert_called_once()
    self.assertEqual(job.name          , result.name)
    self.assertEqual(job.description   , result.description)
    self.assertEqual(job.cronExpression, result.cronExpression)
    self.assertEqual(job.action        , result.action)
