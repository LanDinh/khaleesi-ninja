"""Test the request cleanup."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.models.cleanup.request import RequestCleanupJob


@patch('microservice.models.cleanup.request.LOGGER')
class TestRequestCleanupJob(SimpleTestCase):
  """Test the request cleanup."""

  job = RequestCleanupJob()

  def test_execute_batch(self, *_: MagicMock) -> None :
    """Test executing a batch."""
    # Execute test.
    result = self.job.execute_batch()
    # Assert result.
    self.assertEqual(1, result)

  def test_count_total(self, *_: MagicMock) -> None :
    """Test counting the total."""
    # Execute test.
    result = self.job.count_total()
    # Assert result.
    self.assertEqual(5, result)

  def test_target(self, *_: MagicMock) -> None :
    """Test defining the target."""
    # Execute test & assert result.
    self.job.target_type()
