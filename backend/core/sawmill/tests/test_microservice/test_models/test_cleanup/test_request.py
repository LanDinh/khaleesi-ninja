"""Test the request cleanup."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.models.cleanup.request import RequestCleanupJob


class TestRequestCleanupJob(SimpleTestCase):
  """Test the request cleanup."""

  job = RequestCleanupJob()

  @patch('microservice.models.cleanup.request.Request.objects.filter')
  def test_get_queryset(self, filter_requests: MagicMock) -> None :
    """Test executing a batch."""
    # Execute test.
    self.job.get_queryset()
    # Assert result.
    filter_requests.assert_called_once()
