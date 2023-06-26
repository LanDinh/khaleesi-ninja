"""Test the error logs."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.logging.textLogger import LogLevel
from khaleesi.core.testUtil.grpc import GrpcTestMixin
from khaleesi.core.testUtil.testCase import TransactionTestCase, SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import Error as GrpcError
from microservice.models import Error
from microservice.testUtil import ModelRequestMetadataMixin


@patch('microservice.models.logs.event.parseString')
@patch.object(Error.objects.model, 'logMetadata')
class ErrorManagerTestCase(GrpcTestMixin, TransactionTestCase):
  """Test the error logs objects manager."""

  def testLogError(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging an error."""
    for status in StatusCode:
      for loglevel in LogLevel:
        for userLabel, userType in User.UserType.items():
          with self.subTest(status = status.name, loglevel = loglevel.name, user = userLabel):
            # Prepare data.
            metadata.reset_mock()
            metadata.return_value = {}
            string.return_value = 'parsed-string'
            now = datetime.now(tz = timezone.utc)
            grpcError = GrpcError()
            self.setRequestMetadata(
              requestMetadata = grpcError.requestMetadata,
              now             = now,
              user            = userType,
            )
            grpcError.id             = 'error-id'
            grpcError.status         = status.name
            grpcError.loglevel       = loglevel.name
            grpcError.gate           = 'gate'
            grpcError.service        = 'service'
            grpcError.publicKey      = 'public-key'
            grpcError.publicDetails  = 'public-details'
            grpcError.privateMessage = 'private-message'
            grpcError.privateDetails = 'private-details'
            grpcError.stacktrace     = 'stacktrace'
            # Execute test.
            result = Error.objects.logError(grpcError = grpcError)
            # Assert result.
            metadata.assert_called_once()
            self.assertEqual(grpcError.requestMetadata, metadata.call_args.kwargs['metadata'])
            self.assertEqual([]                       , metadata.call_args.kwargs['errors'])
            self.assertEqual(grpcError.publicDetails  , result.publicDetails)
            self.assertEqual(grpcError.privateMessage , result.privateMessage)
            self.assertEqual(grpcError.privateDetails , result.privateDetails)
            self.assertEqual(grpcError.stacktrace     , result.stacktrace)

  def testLogErrorEmpty(self, metadata: MagicMock, string: MagicMock) -> None :
    """Test logging an empty error."""
    # Prepare data.
    string.return_value   = 'parsed-string'
    metadata.return_value = {}
    grpcError             = GrpcError()
    # Execute test.
    result = Error.objects.logError(grpcError = grpcError)
    # Assert result.
    metadata.assert_called_once()
    self.assertEqual([], metadata.call_args.kwargs['errors'])
    self.assertEqual('', result.metaLoggingErrors)


class ErrorTestCase(ModelRequestMetadataMixin, SimpleTestCase):
  """Test the error logs models."""

  def testToGrpc(self) -> None :
    """Test that general mapping to gRPC works."""
    for status in StatusCode:
      for loglevel in LogLevel:
        for userLabel, userType in User.UserType.items():
          with self.subTest(status = status.name, user = userLabel):
            # Prepare data.
            error = Error(
              errorId        = 'error-id',
              status         = status.name,
              loglevel       = loglevel.name,
              gate           = 'gate',
              service        = 'service',
              publicKey      = 'public-key',
              publicDetails  = 'public-details',
              privateMessage = 'private-message',
              privateDetails = 'private-details',
              stacktrace     = 'stacktrace',
              **self.modelFullRequestMetadata(user = userType),
            )
            # Execute test.
            result = error.toGrpc()
            # Assert result.
            self.assertGrpcRequestMetadata(
              model        = error,
              grpc         = result.error.requestMetadata,
              grpcResponse = result.errorMetadata,
            )
            self.assertEqual(error.errorId       , result.error.id)
            self.assertEqual(error.status        , result.error.status)
            self.assertEqual(error.loglevel      , result.error.loglevel)
            self.assertEqual(error.gate          , result.error.gate)
            self.assertEqual(error.service       , result.error.service)
            self.assertEqual(error.publicKey     , result.error.publicKey)
            self.assertEqual(error.publicDetails , result.error.publicDetails)
            self.assertEqual(error.privateMessage, result.error.privateMessage)
            self.assertEqual(error.privateDetails, result.error.privateDetails)
            self.assertEqual(error.stacktrace    , result.error.stacktrace)

  def testEmptyToGrpcError(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    error = Error(**self.modelEmptyRequestMetadata())
    # Execute test.
    result = error.toGrpc()
    # Assert result.
    self.assertIsNotNone(result)
