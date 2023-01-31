"""Test the event logs."""

# Python.
from datetime import timedelta
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_clocktower_pb2 import Job as GrpcJob
from microservice.models import Job


@patch('microservice.models.job.parse_string')
@patch.object(Job.objects, 'create')
class JobManagerTestCase(SimpleTestCase):
  """Test the event logs objects manager."""

  def test_create_job(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    grpc_job = GrpcJob()
    grpc_job.description                     = 'description'
    grpc_job.cron_expression                 = 'cron'
    grpc_job.action_configuration.batch_size = 1337
    grpc_job.action_configuration.timelimit.FromTimedelta(timedelta(minutes = 13))
    grpc_job.cleanup_configuration.cleanup_delay.FromTimedelta(timedelta(seconds = 42))
    # Execute test.
    Job.objects.create_job(grpc_job = grpc_job)
    # Assert result.
    create.assert_called_once()
    call_args = create.call_args.kwargs
    self.assertEqual(grpc_job.description                    , call_args['description'])
    self.assertEqual(grpc_job.cron_expression                , call_args['cron_expression'])
    self.assertEqual(grpc_job.action_configuration.batch_size, call_args['batch_size'])
    self.assertEqual(
      grpc_job.action_configuration.timelimit.ToTimedelta(),
      call_args['timelimit'],
    )
    self.assertEqual(
      grpc_job.cleanup_configuration.cleanup_delay.ToTimedelta(),
      call_args['cleanup_delay'],
    )

  def test_create_job_enforce_default_batch_size(self, create: MagicMock, *_: MagicMock) -> None :
    """Test creating a new job."""
    # Prepare data.
    grpc_job = GrpcJob()
    # Execute test.
    Job.objects.create_job(grpc_job = grpc_job)
    # Assert result.
    create.assert_called_once()
    call_args = create.call_args.kwargs
    self.assertEqual(1000, call_args['batch_size'])
