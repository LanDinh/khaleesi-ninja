"""Test the log metadata."""

# Python.
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import RequestMetadata, User
from khaleesi.proto.core_sawmill_pb2 import LogRequestMetadata
from tests.models import Metadata, GrpcMetadata


class MetadataMixinTestCase(SimpleTestCase):
  """Test the log metadata."""

  @patch('microservice.models.logs.metadataMixin.parseString')
  @patch('microservice.models.logs.metadataMixin.parseTimestamp')
  def testMetadataFromGrpcForCreation(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test logging metadata."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        grpc = self._createRequestMetadata(
          now       = now,
          timestamp = timestamp,
          string    = string,
          userType  = userType,
        )
        initialError = 'test errors'
        instance               = Metadata()
        instance._state.adding = True  # pylint: disable=protected-access
        # Execute test.
        instance.metadataFromGrpc(grpc = grpc, errors = [ initialError ])
        # Assert result.
        string.assert_called()
        timestamp.assert_called()
        self.assertEqual(now         , instance.metaReportedTimestamp)
        self.assertEqual(userLabel   , instance.metaUserType)
        self.assertEqual(initialError, instance.metaLoggingErrors)

  @patch('microservice.models.logs.metadataMixin.parseString')
  @patch('microservice.models.logs.metadataMixin.parseTimestamp')
  def testMetadataFromGrpcForUpdate(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test logging metadata."""
    for userLabel, userType in [
        (userLabel, userType) for userLabel, userType in User.UserType.items()
        if userType != User.UserType.UNKNOWN
    ]:
      with self.subTest(user = userLabel):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        grpc = self._createRequestMetadata(
          now       = now,
          timestamp = timestamp,
          string    = string,
          userType  = userType,
        )
        initialError = 'test errors'
        instance               = Metadata()
        instance._state.adding = False   # pylint: disable=protected-access
        # Execute test.
        instance.metadataFromGrpc(grpc = grpc, errors = [ initialError ])
        # Assert result.
        timestamp.assert_not_called()
        string.assert_not_called()
        self.assertNotEqual(now         , instance.metaReportedTimestamp)
        self.assertNotEqual(userLabel   , instance.metaUserType)
        self.assertNotEqual(initialError, instance.metaLoggingErrors)

  @patch('microservice.models.logs.metadataMixin.parseString')
  @patch('microservice.models.logs.metadataMixin.parseTimestamp')
  def testMetadataFromGrpcForCreationEmpty(self, timestamp: MagicMock, string: MagicMock) -> None :
    """Test empty input for logging metadata."""
    # Prepare data.
    timestamp.return_value = None
    string.return_value    = 'parsed-string'
    instance               = Metadata()
    instance._state.adding = True  # pylint: disable=protected-access
    # Execute test.
    instance.metadataFromGrpc(grpc = RequestMetadata(), errors = [])
    # Assert result.
    string.assert_called()
    timestamp.assert_called()
    self.assertEqual('', instance.metaLoggingErrors)

  def testMetadataToGrpc(self) -> None :
    """Test transformation to gRPC."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        instance = Metadata()

        instance.metaCallerHttpRequestId = 'http-request-id'
        instance.metaCallerHttpSite      = 'http-site'
        instance.metaCallerHttpPath      = 'http-path'
        instance.metaCallerHttpPodId     = 'http-pod'

        instance.metaUserId   = 'user-id'
        instance.metaUserType = userLabel

        instance.metaReportedTimestamp = now
        instance.metaLoggedTimestamp   = now
        instance.metaLoggingErrors     = 'errors'

        requestMetadata = RequestMetadata()
        logMetadata     = LogRequestMetadata()

        # Execute test.
        instance.metadataToGrpc(requestMetadata = requestMetadata, logMetadata = logMetadata)
        # Assert result.
        self.assertEqual(instance.metaCallerHttpRequestId, requestMetadata.httpCaller.requestId)
        self.assertEqual(instance.metaCallerHttpSite     , requestMetadata.httpCaller.site)
        self.assertEqual(instance.metaCallerHttpPath     , requestMetadata.httpCaller.path)
        self.assertEqual(instance.metaCallerHttpPodId    , requestMetadata.httpCaller.podId)

        self.assertEqual(instance.metaUserId, requestMetadata.user.id)
        self.assertEqual(userType           , requestMetadata.user.type)
        self.assertEqual(
          instance.metaReportedTimestamp,
          requestMetadata.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
        )

        self.assertEqual(
          instance.metaLoggedTimestamp,
          logMetadata.loggedTimestamp.ToDatetime().replace(tzinfo = timezone.utc),
        )
        self.assertEqual(instance.metaLoggingErrors  , logMetadata.errors)

  def testMetadataToGrpcEmpty(self) -> None :
    """Test transformation to gRPC."""
    # Prepare data.
    instance = Metadata()
    requestMetadata = RequestMetadata()
    logMetadata     = LogRequestMetadata()
    # Execute test & assert result.
    instance.metadataToGrpc(requestMetadata = requestMetadata, logMetadata = logMetadata)

  def _createRequestMetadata(
      self, *,
      now      : datetime,
      timestamp: MagicMock,
      string   : MagicMock,
      userType : 'User.UserType.V',
  ) -> RequestMetadata :
    """Utility for creating fully populated request metadata objects."""
    timestamp.return_value = now
    string.return_value    = 'parsed-string'
    grpc = RequestMetadata()
    grpc.timestamp.FromDatetime(now)

    grpc.httpCaller.requestId = 'http-request-id'
    grpc.httpCaller.path      = 'http-path'
    grpc.httpCaller.site      = 'http-site'
    grpc.httpCaller.podId     = 'http-pod'

    grpc.user.id   = 'user-id'
    grpc.user.type = userType

    return grpc


class GrpcMetadataMixinTestCase(SimpleTestCase):
  """Test the log metadata."""

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataFromGrpc')
  @patch('microservice.models.logs.metadataMixin.parseString')
  def testMetadataFromGrpcForCreation(self, string: MagicMock, parent: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    grpc = self._createRequestMetadata(string = string)
    instance               = GrpcMetadata()
    instance._state.adding = True  # pylint: disable=protected-access
    # Execute test.
    instance.metadataFromGrpc(grpc = grpc, errors = [])
    # Assert result.
    parent.assert_called_once()
    string.assert_called()

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataFromGrpc')
  @patch('microservice.models.logs.metadataMixin.parseString')
  def testMetadataFromGrpcForUpdate(self, string: MagicMock, parent: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    grpc = self._createRequestMetadata(string = string)
    instance               = GrpcMetadata()
    instance._state.adding = False   # pylint: disable=protected-access
    # Execute test.
    instance.metadataFromGrpc(grpc = grpc, errors = [])
    # Assert result.
    parent.assert_called_once()
    string.assert_not_called()

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataFromGrpc')
  @patch('microservice.models.logs.metadataMixin.parseString')
  def testMetadataFromGrpcForCreationEmpty(self, string: MagicMock, parent: MagicMock) -> None :
    """Test empty input for logging metadata."""
    # Prepare data.
    string.return_value    = 'parsed-string'
    instance               = GrpcMetadata()
    instance._state.adding = True  # pylint: disable=protected-access
    # Execute test.
    instance.metadataFromGrpc(grpc = RequestMetadata(), errors = [])
    # Assert result.
    parent.assert_called_once()
    self.assertEqual('', instance.metaLoggingErrors)

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataToGrpc')
  def testMetadataToGrpc(self, parent: MagicMock) -> None :
    """Test transformation to gRPC."""
    # Prepare data.
    instance = GrpcMetadata()

    instance.metaCallerGrpcRequestId = 'grpc-request-id'
    instance.metaCallerGrpcSite      = 'grpc-site'
    instance.metaCallerGrpcApp       = 'service'
    instance.metaCallerGrpcService   = 'service'
    instance.metaCallerGrpcMethod    = 'method'
    instance.metaCallerGrpcPodId     = 'grpc-pod'

    requestMetadata = RequestMetadata()
    logMetadata     = LogRequestMetadata()

    # Execute test.
    instance.metadataToGrpc(requestMetadata = requestMetadata, logMetadata = logMetadata)
    # Assert result.
    parent.assert_called_once()
    self.assertEqual(instance.metaCallerGrpcRequestId, requestMetadata.grpcCaller.requestId)
    self.assertEqual(instance.metaCallerGrpcSite     , requestMetadata.grpcCaller.site)
    self.assertEqual(instance.metaCallerGrpcApp      , requestMetadata.grpcCaller.app)
    self.assertEqual(instance.metaCallerGrpcService  , requestMetadata.grpcCaller.service)
    self.assertEqual(instance.metaCallerGrpcMethod   , requestMetadata.grpcCaller.method)
    self.assertEqual(instance.metaCallerGrpcPodId    , requestMetadata.grpcCaller.podId)

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataToGrpc')
  def testMetadataToGrpcEmpty(self, parent: MagicMock) -> None :
    """Test transformation to gRPC."""
    # Prepare data.
    instance = GrpcMetadata()
    requestMetadata = RequestMetadata()
    logMetadata     = LogRequestMetadata()

    # Execute test.
    instance.metadataToGrpc(requestMetadata = requestMetadata, logMetadata = logMetadata)
    # Assert result.
    parent.assert_called_once()

  def _createRequestMetadata(self, *, string: MagicMock) -> RequestMetadata :
    """Utility for creating fully populated request metadata objects."""
    string.return_value    = 'parsed-string'
    grpc = RequestMetadata()

    grpc.grpcCaller.requestId = 'grpc-request'
    grpc.grpcCaller.site      = 'grpc-site'
    grpc.grpcCaller.app       = 'service'
    grpc.grpcCaller.service   = 'service'
    grpc.grpcCaller.method    = 'method'
    grpc.grpcCaller.podId     = 'grpc-pod'

    return grpc