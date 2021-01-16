"""Test the default manager."""

# Python.
import uuid
from typing import cast, Dict, Any
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.language_type import Language
from common.models import LogRequest
from test_util.models.log.request import TestLogRequestIntegrationMixin
from test_util.test import SimpleTestCase, TestCase


class LogRequestDefaultManagerUnitTests(SimpleTestCase):
  """Unit tests for the default manager."""

  def test_create_and_get(self) -> None :
    """Test if creation works."""
    for optional_args in [
        cast(Dict[str, Any], {}),
        {'client_id': MagicMock()},
        {'language': MagicMock()},
        {'client_id': MagicMock(), 'language': MagicMock()},
    ]:
      with patch.object(LogRequest.objects, 'model', return_value = MagicMock()) as model:
        backend_request = MagicMock()
        backend_request.kwargs = {}
        with self.subTest(optional_args = optional_args):
          # Perform test.
          LogRequest.objects.create_and_get(
              backend_request = backend_request,
              backend_body = {},
              frontend_route = MagicMock(),
              frontend_parameters = MagicMock(),
              frontend_service = MagicMock(),
              frontend_feature = MagicMock(),
              frontend_body = MagicMock(),
              **optional_args,
          )
          # Assert result.
          model.return_value.save.assert_called_once_with()


class LogRequestDefaultManagerIntegrationTests(TestCase, TestLogRequestIntegrationMixin):
  """Unit tests for the default manager."""

  def test_create_and_get_minimum_input(self) -> None :
    """Test if creation works."""
    # Perform test.
    log = LogRequest.objects.create_and_get(**self.create_and_get_minimum_input())
    # Assert result.
    self.assert_minimum_input_for_log(log = log)
    self.assertIsNone(log.client_id)
    self.assertIsNone(log.language)

  def test_create_and_get_client_id(self) -> None :
    """Test if creation works."""
    # Prepare data.
    client_id = uuid.uuid4()
    # Perform test.
    log = LogRequest.objects.create_and_get(
        client_id = client_id,
        **self.create_and_get_minimum_input(),
    )
    # Assert result.
    self.assert_minimum_input_for_log(log = log)
    self.assertEqual(client_id, log.client_id)
    self.assertIsNone(log.language)

  def test_create_and_get_language(self) -> None :
    """Test if creation works."""
    for language in Language:
      with self.subTest(language = language):
        # Perform test.
        log = LogRequest.objects.create_and_get(
            language = language,
            **self.create_and_get_minimum_input(),
        )
        # Assert result.
        self.assert_minimum_input_for_log(log = log)
        self.assertIsNone(log.client_id)
        self.assertEqual(language.name, log.language)
        log.delete()

  def test_create_and_get_full_input(self) -> None :
    """Test if creation works."""
    for language in Language:
      with self.subTest(language = language):
        # Prepare data.
        client_id = uuid.uuid4()
        # Perform test.
        log = LogRequest.objects.create_and_get(
            client_id = client_id,
            language = language,
            **self.create_and_get_minimum_input(),
        )
        # Assert result.
        self.assert_minimum_input_for_log(log = log)
        self.assertEqual(client_id, log.client_id)
        self.assertEqual(language.name, log.language)

  def assert_minimum_input_for_log(self, *, log: LogRequest) -> None :
    """Assert the minimum input of the log."""
    self.assertEqual('backend_route', log.backend_route)
    self.assertEqual('{"backend": "parameters"}', log.backend_parameters)
    self.assertEqual('TRANSLATE', log.backend_service)
    self.assertEqual('backend_feature', log.backend_feature)
    self.assertEqual('{"backend": "body"}', log.backend_body)
    self.assertEqual('frontend_route', log.frontend_route)
    self.assertEqual('frontend_parameters', log.frontend_parameters)
    self.assertEqual('TRANSLATE', log.frontend_service)
    self.assertEqual('frontend_feature', log.frontend_feature)
    self.assertEqual('frontend_body', log.frontend_body)
    self.assertIsNone(log.user)
    self.assertIsNone(log.end_time)
    self.assertIsNone(log.response_code)
