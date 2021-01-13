"""Test LogRequest model."""

# Python.
from dataclasses import asdict
from unittest.mock import MagicMock

# khaleesi.ninja.
from common.models import LogRequest
from test_util.models.log.request import TestLogRequestIntegrationMixin
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences,PyTypeHints
class LogRequestUnitTests(SimpleTestCase, TestUserUnitMixin):
  """Unit tests for LogRequest."""

  def test_finalize(self) -> None :
    """Test finalization."""
    for params in self.params():
      with self.subTest(asdict(params)):
        # Prepare data.
        log = LogRequest()
        log.save = MagicMock()  # type: ignore[assignment]
        user, _ = self.create_user(params = params)
        response_code = 200
        # Perform test.
        log.finalize(user = user, response_code = response_code)
        # Assert result.
        self.assertEqual(user, log.user)
        self.assertEqual(response_code, log.response_code)
        self.assertIsNotNone(log.end_time)


class LogRequestIntegrationTests(
    TestCase,
    TestUserIntegrationMixin,
    TestLogRequestIntegrationMixin,
):
  """Unit tests for LogRequest."""

  def test_finalize(self) -> None :
    """Test finalization."""
    for params in self.params():
      with self.subTest(asdict(params)):
        # Prepare data.
        log = LogRequest.objects.create_and_get(**self.create_and_get_minimum_input())
        user, _ = self.create_user(params = params)
        response_code = 200
        # Perform test.
        log.finalize(user = user, response_code = response_code)
        # Assert result.
        self.assertEqual(user, log.user)
        self.assertEqual(response_code, log.response_code)
        self.assertIsNotNone(log.end_time)
        log.delete()
        user.delete()
