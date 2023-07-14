"""Test the gRPC server command."""

# Python.
from typing import cast
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.shared.exceptions import KhaleesiException
from khaleesi.core.testUtil.exceptions import (
  defaultKhaleesiException,
  defaultException,
)
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.management.commands.grpcserver import Command


class GrpcServerTestCase(SimpleTestCase):
  """Test the gRPC server command."""

  command = Command()


  @patch.dict('khaleesi.management.commands.grpcserver.khaleesiSettings', {
      'STARTUP': {
          'MIGRATIONS_BEFORE_SERVER_START': {
              'REQUIRED' : True,
              'MIGRATION': 'migration-name',
          },
      },
  })
  def testInitMigration(self) -> None :
    """Test server start if preliminary migrations need to be applied."""
    self._executeTests(migrationCalls = 3)

  def testRegular(self) -> None :
    """Test regular server start."""
    self._executeTests(migrationCalls = 2)

  def _executeTests(self, *, migrationCalls: int) -> None :
    """Execute the test cases."""
    for name, method in [
        ('ok'                     , self._executeOkTest),
        ('khaleesi exception'     , self._executeKhaleesiExceptionTest),
        ('other exception wrapped', self._executeOtherExceptionWrappedTest),
        ('other exception'        , self._executeOtherExceptionTest),
    ]:
      with self.subTest(name = name):
        method(migrationCalls = migrationCalls)  # pylint: disable=no-value-for-parameter

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _executeOkTest(
      self,
      migrate      : MagicMock,
      server       : MagicMock,
      metricsServer: MagicMock,
      singleton    : MagicMock,
      *,
      migrationCalls: int,
  ) -> None :
    """Test the ok case."""
    # Execute test.
    self.command.khaleesiHandle()
    # Assert result.
    singleton.structuredLogger.logHttpRequest.assert_called_once()
    singleton.structuredLogger.logHttpResponse.assert_called_once()
    self.assertEqual(3, singleton.structuredLogger.logSystemGrpcRequest.call_count)
    self.assertEqual(3, singleton.structuredLogger.logSystemGrpcResponse.call_count)
    self.assertEqual(migrationCalls, migrate.handle.call_count)
    server.return_value.start.assert_called_once()
    metricsServer.assert_called_once()

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _executeKhaleesiExceptionTest(
      self,
      migrate      : MagicMock,
      server       : MagicMock,
      metricsServer: MagicMock,
      singleton    : MagicMock,
      *,
      migrationCalls: int,
  ) -> None :
    """Test khaleesi exceptions."""
    for status in StatusCode:
      for loglevel in LogLevel:
        with self.subTest(status = status.name, loglevel = loglevel.name):
          # Prepare test.
          migrate.reset_mock()
          server.reset_mock()
          metricsServer.reset_mock()
          singleton.reset_mock()
          exception = defaultKhaleesiException(status = status, loglevel = loglevel)
          server.return_value.start.side_effect = exception
          with self.assertRaises(KhaleesiException) as raisedException:
            # Execute test.
            self.command.khaleesiHandle()
            # Assert result.
            singleton.structuredLogger.logHttpRequest.assert_called_once()
            singleton.structuredLogger.logHttpResponse.assert_called_once()
            self.assertEqual(3, singleton.structuredLogger.logSystemGrpcRequest.call_count)
            self.assertEqual(3, singleton.structuredLogger.logSystemGrpcResponse.call_count)
            self.assertEqual(migrationCalls, migrate.handle.call_count)
            server.return_value.start.assert_called_once_with()
            metricsServer.assert_called_once()
            raisedKhaleesiException = cast(KhaleesiException, raisedException)
            self.assertEqual(exception.status  , raisedKhaleesiException.status)  # pylint: disable=no-member
            self.assertEqual(exception.loglevel, raisedKhaleesiException.loglevel)  # pylint: disable=no-member

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _executeOtherExceptionTest(
      self,
      migrate      : MagicMock,
      server       : MagicMock,
      metricsServer: MagicMock,
      singleton    : MagicMock,
      *,
      migrationCalls: int,
  ) -> None :
    """Test the other exception case."""
    # Prepare test.
    exception = defaultException()
    server.return_value.waitForTermination.side_effect = exception
    with self.assertRaises(Exception):
      # Execute test.
      self.command.khaleesiHandle()
      # Assert result.
      singleton.structuredLogger.logHttpRequest.assert_called_once()
      singleton.structuredLogger.logHttpResponse.assert_called_once()
      self.assertEqual(3, singleton.structuredLogger.logSystemGrpcRequest.call_count)
      self.assertEqual(3, singleton.structuredLogger.logSystemGrpcResponse.call_count)
      self.assertEqual(migrationCalls, migrate.handle.call_count)
      server.return_value.start.assert_called_once_with()
      metricsServer.assert_called_once()

  @patch('khaleesi.management.commands.grpcserver.SINGLETON')
  @patch('khaleesi.management.commands.grpcserver.start_http_server')
  @patch('khaleesi.management.commands.grpcserver.Server')
  @patch('khaleesi.management.commands.grpcserver.DjangoMigrateCommand')
  def _executeOtherExceptionWrappedTest(
      self,
      migrate      : MagicMock,
      server       : MagicMock,
      metricsServer: MagicMock,
      singleton    : MagicMock,
      *,
      migrationCalls: int,
  ) -> None :
    """Test other exceptions in the wrapped case."""
    # Prepare test.
    exception = defaultException()
    server.return_value.start.side_effect = exception
    with self.assertRaises(KhaleesiException) as raisedException:
      # Execute test.
      self.command.khaleesiHandle()
      # Assert result.
      singleton.structuredLogger.logHttpRequest.assert_called_once()
      singleton.structuredLogger.logHttpResponse.assert_called_once()
      self.assertEqual(3, singleton.structuredLogger.logSystemGrpcRequest.call_count)
      self.assertEqual(3, singleton.structuredLogger.logSystemGrpcResponse.call_count)
      self.assertEqual(migrationCalls, migrate.handle.call_count)
      server.return_value.start.assert_called_once_with()
      metricsServer.assert_called_once()
      raisedKhaleesiException = cast(KhaleesiException, raisedException)
      self.assertEqual(StatusCode.INTERNAL, raisedKhaleesiException.status)  # pylint: disable=no-member
      self.assertEqual(LogLevel.FATAL     , raisedKhaleesiException.loglevel)  # pylint: disable=no-member
