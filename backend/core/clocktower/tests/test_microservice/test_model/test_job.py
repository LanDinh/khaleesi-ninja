"""Test the event logs."""

# Python.
from datetime import timedelta
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.shared.exceptions import DbObjectNotFoundException, DbObjectTwinException
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import IdMessage
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob
from microservice.models import Job


@patch('microservice.models.job.parse_string')
class JobManagerTestCase(SimpleTestCase):
  """Test the event logs objects manager."""

  @patch.object(Job.objects, 'create')
  def test_create_job(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    grpc_job = GrpcJob()
    grpc_job.description                   = 'description'
    grpc_job.cronExpression                = 'cron'
    grpc_job.actionConfiguration.batchSize = 1337
    grpc_job.actionConfiguration.timelimit.FromTimedelta(timedelta(minutes = 13))
    grpc_job.cleanupConfiguration.cleanupDelay.FromTimedelta(timedelta(seconds = 42))
    # Execute test.
    Job.objects.create_job(grpc_job = grpc_job)
    # Assert result.
    create.assert_called_once()
    call_args = create.call_args.kwargs
    self.assertEqual(grpc_job.description   , call_args['description'])
    self.assertEqual(grpc_job.cronExpression, call_args['cron_expression'])
    self.assertEqual(grpc_job.actionConfiguration.batchSize              , call_args['batch_size'])
    self.assertEqual(grpc_job.actionConfiguration.timelimit.ToTimedelta(), call_args['timelimit'])
    self.assertEqual(
      grpc_job.cleanupConfiguration.cleanupDelay.ToTimedelta(),
      call_args['cleanup_delay'],
    )

  @patch.object(Job.objects, 'create')
  def test_create_job_enforce_default_values(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    grpc_job = GrpcJob()
    # Execute test.
    Job.objects.create_job(grpc_job = grpc_job)
    # Assert result.
    create.assert_called_once()
    call_args = create.call_args.kwargs
    self.assertEqual(1000                , call_args['batch_size'])
    self.assertEqual(timedelta(hours = 1), call_args['timelimit'])

  @patch.object(Job.objects, 'get')
  def test_get_job_request(self, get: MagicMock, *_: MagicMock) -> None :
    """Test getting a job request."""
    # Prepare data.
    id_message = IdMessage()
    get.return_value = Job()
    # Execute test.
    Job.objects.get_job_request(id_message = id_message)
    # Assert result.
    get.assert_called_once_with(job_id = id_message.id)

  @patch.object(Job.objects, 'get')
  def test_get_job_request_not_found(self, get: MagicMock, *_: MagicMock) -> None :
    """Test getting a job request."""
    # Prepare data.
    get.side_effect = Job.DoesNotExist()
    # Execute test & assert result.
    with self.assertRaises(DbObjectNotFoundException):
      Job.objects.get_job_request(id_message = IdMessage())

  @patch.object(Job.objects, 'get')
  def test_get_job_request_twins(self, get: MagicMock, *_: MagicMock) -> None :
    """Test getting a job request."""
    # Prepare data.
    get.side_effect = Job.MultipleObjectsReturned()
    # Execute test & assert result.
    with self.assertRaises(DbObjectTwinException):
      Job.objects.get_job_request(id_message = IdMessage())
