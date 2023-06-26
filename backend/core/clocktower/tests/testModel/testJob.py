"""Test the event logs."""

# Python.
from datetime import timedelta
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import DbObjectNotFoundException, DbObjectTwinException
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import IdMessage
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob
from microservice.models import Job


@patch('microservice.models.job.parseString')
class JobManagerTestCase(SimpleTestCase):
  """Test the event logs objects manager."""

  @patch.object(Job.objects, 'create')
  def testCreateJob(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    grpcJob = GrpcJob()
    grpcJob.description                   = 'description'
    grpcJob.cronExpression                = 'cron'
    grpcJob.actionConfiguration.batchSize = 1337
    grpcJob.actionConfiguration.timelimit.FromTimedelta(timedelta(minutes = 13))
    grpcJob.cleanupConfiguration.cleanupDelay.FromTimedelta(timedelta(seconds = 42))
    # Execute test.
    Job.objects.createJob(grpcJob = grpcJob)
    # Assert result.
    create.assert_called_once()
    callArgs = create.call_args.kwargs
    self.assertEqual(grpcJob.description   , callArgs['description'])
    self.assertEqual(grpcJob.cronExpression, callArgs['cronExpression'])
    self.assertEqual(grpcJob.actionConfiguration.batchSize              , callArgs['batchSize'])
    self.assertEqual(grpcJob.actionConfiguration.timelimit.ToTimedelta(), callArgs['timelimit'])
    self.assertEqual(
      grpcJob.cleanupConfiguration.cleanupDelay.ToTimedelta(),
      callArgs['cleanupDelay'],
    )

  @patch.object(Job.objects, 'create')
  def testCreateJobEnforceDefaultValues(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    grpcJob = GrpcJob()
    # Execute test.
    Job.objects.createJob(grpcJob = grpcJob)
    # Assert result.
    create.assert_called_once()
    callArgs = create.call_args.kwargs
    self.assertEqual(1000                , callArgs['batchSize'])
    self.assertEqual(timedelta(hours = 1), callArgs['timelimit'])

  @patch.object(Job.objects, 'get')
  def testGetJobRequest(self, get: MagicMock, *_: MagicMock) -> None :
    """Test getting a job request."""
    # Prepare data.
    idMessage = IdMessage()
    get.return_value = Job()
    # Execute test.
    Job.objects.getJobRequest(idMessage = idMessage)
    # Assert result.
    get.assert_called_once_with(jobId = idMessage.id)

  @patch.object(Job.objects, 'get')
  def testGetJobRequestNotFound(self, get: MagicMock, *_: MagicMock) -> None :
    """Test getting a job request."""
    # Prepare data.
    get.side_effect = Job.DoesNotExist()
    # Execute test & assert result.
    with self.assertRaises(DbObjectNotFoundException):
      Job.objects.getJobRequest(idMessage = IdMessage())

  @patch.object(Job.objects, 'get')
  def testGetJobRequestTwins(self, get: MagicMock, *_: MagicMock) -> None :
    """Test getting a job request."""
    # Prepare data.
    get.side_effect = Job.MultipleObjectsReturned()
    # Execute test & assert result.
    with self.assertRaises(DbObjectTwinException):
      Job.objects.getJobRequest(idMessage = IdMessage())
