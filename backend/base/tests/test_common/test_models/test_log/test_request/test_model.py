"""Test LogRequest model."""

# Python.
from dataclasses import asdict
from typing import cast
from unittest.mock import MagicMock, patch

# khaleesi.ninja.
from common.models import LogRequest, User
from test_util.models.log.request import TestLogRequestIntegrationMixin
from test_util.models.user import (
    TestUserUnitMixin,
    TestUserIntegrationMixin,
    Parameters,
)
from test_util.test import SimpleTestCase, TransactionTestCase


# noinspection PyMissingOrEmptyDocstring,PyUnresolvedReferences,PyTypeHints
class LogRequestUnitTests(SimpleTestCase, TestUserUnitMixin):
  """Unit tests for LogRequest."""

  def test_finalize(self) -> None :
    """Test finalization."""
    with patch.object(User.objects, 'db_manager') as manager:
      for params in self.params():
        with self.subTest(asdict(params)):
          # Prepare data.
          log = LogRequest()
          log.save = MagicMock()  # type: ignore[assignment]
          user = self.create_user(params = params)
          manager.return_value = MagicMock()
          manager.return_value.get = MagicMock(return_value = user)
          response_code = 200
          # Perform test.
          log.finalize(user = user, response_code = response_code)
          # Assert result.
          manager.assert_called_once_with('logging')
          manager.return_value.get.assert_called_once_with(username = user.username)
          manager.reset_mock()
          self.assertEqual(user, log.user)
          self.assertEqual(response_code, log.response_code)
          self.assertIsNotNone(log.end_time)

  def create_user(self, *, params: Parameters) -> User :
    """Create a unit test user according to requirements, mock super methods."""
    user = User(username = params.creates.username)
    user = self._attach_common_properties(mock = cast(MagicMock, user), params = params)
    return user


class LogRequestIntegrationTests(
    TransactionTestCase,
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
        user = self.create_user(params = params)
        response_code = 200
        # Perform test.
        log.finalize(user = user, response_code = response_code)
        # Assert result.
        self.assertEqual(user, log.user)
        self.assertEqual(response_code, log.response_code)
        self.assertIsNotNone(log.end_time)
        log.delete()
        user.delete()
