"""Test the gRPC server command."""

# Python.
from typing import cast
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.text_logger import LogLevel
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.test_util.exceptions import (
  default_khaleesi_exception,
  default_exception,
)
from khaleesi.core.test_util.test_case import SimpleTestCase
from khaleesi.management.commands.grpcserver import Command


class GrpcServerTestCase(SimpleTestCase):
  """Test the gRPC server command."""

  command = Command()


  @patch.dict('khaleesi.management.commands.grpcserver.khaleesi_settings', {
      'STARTUP': {
          'MIGRATIONS_BEFORE_SERVER_START': {
              'REQUIRED' : True,
              'MIGRATION': 'migration-name',
          },
      },
  })
  def test_init_migration(self) -> None :
    """Test server start if preliminary migrations need to be applied."""
    self._execute_tests(migration_calls = 3)

  def test_regular(self) -> None :
    """Test regular server start."""
    self._execute_tests(migration_calls = 2)

  def _execute_tests(self, *, migration_calls: int) -> None :
    """Execute the test cases."""
    for name, method in [
        ('ok'                     , self._execute_ok_test),
        ('khaleesi exception'     , self._execute_khaleesi_exception_test),
        ('other exception wrapped', self._execute_other_exception_wrapped_test),
        ('other exception'        , self._execute_other_exception_test),
    ]:
      with self.subTest(name = name):
        method(migration_calls = migration_calls)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _execute_ok_test(
      self,
      migrate       : MagicMock,
      server        : MagicMock,
      metrics_server: MagicMock,
      singleton     : MagicMock,
      *,
      migration_calls: int,
  ) -> None :
    """Test the ok case."""
    # Execute test.
    self.command.khaleesi_handle()
    # Assert result.
    singleton.structured_logger.log_system_http_request.assert_called_once()
    singleton.structured_logger.log_system_http_response.assert_called_once()
    self.assertEqual(3, singleton.structured_logger.log_system_grpc_request.call_count)
    self.assertEqual(3, singleton.structured_logger.log_system_grpc_response.call_count)
    self.assertEqual(migration_calls, migrate.handle.call_count)
    server.return_value.start.assert_called_once()
    metrics_server.assert_called_once()

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _execute_khaleesi_exception_test(
      self,
      migrate       : MagicMock,
      server        : MagicMock,
      metrics_server: MagicMock,
      singleton     : MagicMock,
      *,
      migration_calls: int,
  ) -> None :
    """Test khaleesi exceptions."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare test.
          migrate.reset_mock()
          server.reset_mock()
          metrics_server.reset_mock()
          singleton.reset_mock()
          exception = default_khaleesi_exception(status = status, loglevel = loglevel)
          server.return_value.start.side_effect = exception
          with self.assertRaises(KhaleesiException) as raised_exception:
            # Execute test.
            self.command.khaleesi_handle()
            # Assert result.
            singleton.structured_logger.log_system_http_request.assert_called_once()
            singleton.structured_logger.log_system_http_response.assert_called_once()
            self.assertEqual(3, singleton.structured_logger.log_system_grpc_request.call_count)
            self.assertEqual(3, singleton.structured_logger.log_system_grpc_response.call_count)
            self.assertEqual(migration_calls, migrate.handle.call_count)
            server.return_value.start.assert_called_once_with()
            metrics_server.assert_called_once()
            raised_khaleesi_exception = cast(KhaleesiException, raised_exception)
            self.assertEqual(exception.status  , raised_khaleesi_exception.status)  # pylint: disable=no-member
            self.assertEqual(exception.loglevel, raised_khaleesi_exception.loglevel)  # pylint: disable=no-member

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _execute_other_exception_test(
      self,
      migrate       : MagicMock,
      server        : MagicMock,
      metrics_server: MagicMock,
      singleton     : MagicMock,
      *,
      migration_calls: int,
  ) -> None :
    """Test the other exception case."""
    # Prepare test.
    exception = default_exception()
    server.return_value.wait_for_termination.side_effect = exception
    with self.assertRaises(Exception):
      # Execute test.
      self.command.khaleesi_handle()
      # Assert result.
      singleton.structured_logger.log_system_http_request.assert_called_once()
      singleton.structured_logger.log_system_http_response.assert_called_once()
      self.assertEqual(3, singleton.structured_logger.log_system_grpc_request.call_count)
      self.assertEqual(3, singleton.structured_logger.log_system_grpc_response.call_count)
      self.assertEqual(migration_calls, migrate.handle.call_count)
      server.return_value.start.assert_called_once_with()
      metrics_server.assert_called_once()

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _execute_other_exception_wrapped_test(
      self,
      migrate       : MagicMock,
      server        : MagicMock,
      metrics_server: MagicMock,
      singleton     : MagicMock,
      *,
      migration_calls: int,
  ) -> None :
    """Test other exceptions in the wrapped case."""
    # Prepare test.
    exception = default_exception()
    server.return_value.start.side_effect = exception
    with self.assertRaises(KhaleesiException) as raised_exception:
      # Execute test.
      self.command.khaleesi_handle()
      # Assert result.
      singleton.structured_logger.log_system_http_request.assert_called_once()
      singleton.structured_logger.log_system_http_response.assert_called_once()
      self.assertEqual(3, singleton.structured_logger.log_system_grpc_request.call_count)
      self.assertEqual(3, singleton.structured_logger.log_system_grpc_response.call_count)
      self.assertEqual(migration_calls, migrate.handle.call_count)
      server.return_value.start.assert_called_once_with()
      metrics_server.assert_called_once()
      raised_khaleesi_exception = cast(KhaleesiException, raised_exception)
      self.assertEqual(StatusCode.INTERNAL, raised_khaleesi_exception.status)  # pylint: disable=no-member
      self.assertEqual(LogLevel.FATAL     , raised_khaleesi_exception.loglevel)  # pylint: disable=no-member
