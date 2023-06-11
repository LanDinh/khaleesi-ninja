"""Test the core maid service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.core.service.maid import Service
from khaleesi.models.job import JobExecution
from khaleesi.proto.core_pb2 import IdRequest


@patch('khaleesi.core.service.maid.LOGGER')
class MaidServiceTestCase(SimpleTestCase):
  """Test the core maid service."""

  service = Service()

  @patch.object(JobExecution.objects, 'stop_job')
  def test_abort_batch_job(self, stop_job: MagicMock, *_: MagicMock) -> None :
    """Test aborting a specific job."""
    # Execute test.
    self.service.AbortBatchJob(IdRequest(), MagicMock())
    # Assert result.
    stop_job.assert_called_once()
