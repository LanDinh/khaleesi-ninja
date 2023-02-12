"""Test the request cleanup."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.proto.core_pb2 import JobCleanupRequest
from microservice.models.cleanup import CleanupJob
from tests.models import Metadata


class TestRequestCleanupJob(SimpleTestCase):
  """Test the request cleanup."""

  @patch('tests.test_microservice.test_models.test_cleanup.Metadata.objects.filter')
  def test_get_queryset(self, filter_requests: MagicMock) -> None :
    """Test executing a batch."""
    # Prepare data.
    request = JobCleanupRequest()
    request.action_configuration.batch_size = 1
    job: CleanupJob[Metadata] = CleanupJob(model = Metadata, request = request)
    # Execute test.
    job.get_queryset()
    # Assert result.
    filter_requests.assert_called_once()
