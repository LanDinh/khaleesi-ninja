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
    grpc                   = RequestMetadata()
    instance               = Metadata()
    instance._state.adding = True  # pylint: disable=protected-access
    # Execute test.
    instance.metadataFromGrpc(grpc = grpc, errors = [])
    # Assert result.
    self.assertEqual('', instance.metaLoggingErrors)

  def testMetadataToGrpc(self) -> None :
    """Test transformation to gRPC."""
    for userLabel, userType in User.UserType.items():
      with self.subTest(user = userLabel):
        # Prepare data.
        now = datetime.now(tz = timezone.utc)
        instance = Metadata()

        instance.metaCallerHttpRequestId    = 'http-request-id'
        instance.metaCallerHttpKhaleesiGate = 'http-gate'
        instance.metaCallerHttpPath         = 'http-path'
        instance.metaCallerHttpPodId        = 'http-pod'

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
        self.assertEqual(instance.metaCallerHttpRequestId   , requestMetadata.httpCaller.requestId)
        self.assertEqual(
          instance.metaCallerHttpKhaleesiGate,
          requestMetadata.httpCaller.khaleesiGate,
        )
        self.assertEqual(instance.metaCallerHttpPath        , requestMetadata.httpCaller.path)
        self.assertEqual(instance.metaCallerHttpPodId       , requestMetadata.httpCaller.podId)

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

    grpc.httpCaller.requestId    = 'http-request-id'
    grpc.httpCaller.path         = 'http-path'
    grpc.httpCaller.khaleesiGate = 'http-gate'
    grpc.httpCaller.podId        = 'http-pod'

    grpc.user.id    = 'user-id'
    grpc.user.type  = userType

    return grpc


class GrpcMetadataMixinTestCase(SimpleTestCase):
  """Test the log metadata."""

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataFromGrpc')
  @patch('microservice.models.logs.metadataMixin.parseString')
  def testMetadataFromGrpcForCreation(self, string: MagicMock, parent: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    grpc     = self._createRequestMetadata(string = string)
    instance = GrpcMetadata()
    # Execute test.
    instance.metadataFromGrpc(grpc = grpc, errors = [])
    # Assert result.
    parent.assert_called_once()

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataFromGrpc')
  @patch('microservice.models.logs.metadataMixin.parseString')
  def testMetadataFromGrpcForUpdate(self, string: MagicMock, parent: MagicMock) -> None :
    """Test logging metadata."""
    # Prepare data.
    grpc     = self._createRequestMetadata(string = string)
    instance = GrpcMetadata()
    instance.pk = 1337
    # Execute test.
    instance.metadataFromGrpc(grpc = grpc, errors = [])
    # Assert result.
    parent.assert_called_once()

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataFromGrpc')
  @patch('microservice.models.logs.metadataMixin.parseString')
  def testMetadataFromGrpcForCreationEmpty(self, _: MagicMock, parent: MagicMock) -> None :
    """Test empty input for logging metadata."""
    # Prepare data.
    instance = GrpcMetadata()
    # Execute test.
    instance.metadataFromGrpc(grpc = RequestMetadata(), errors = [])
    # Assert result.
    parent.assert_called_once()

  @patch('microservice.models.logs.metadataMixin.MetadataMixin.metadataToGrpc')
  def testMetadataToGrpc(self, parent: MagicMock) -> None :
    """Test transformation to gRPC."""
    # Prepare data.
    instance = GrpcMetadata()

    instance.metaCallerGrpcRequestId       = 'grpc-request-id'
    instance.metaCallerGrpcKhaleesiGate    = 'grpc-gate'
    instance.metaCallerGrpcKhaleesiService = 'grpc-service'
    instance.metaCallerGrpcGrpcService     = 'grpc-service'
    instance.metaCallerGrpcGrpcMethod      = 'grpc-method'
    instance.metaCallerGrpcPodId           = 'grpc-pod'

    requestMetadata = RequestMetadata()
    logMetadata     = LogRequestMetadata()

    # Execute test.
    instance.metadataToGrpc(requestMetadata = requestMetadata, logMetadata = logMetadata)
    # Assert result.
    parent.assert_called_once()
    self.assertEqual(instance.metaCallerGrpcRequestId   , requestMetadata.grpcCaller.requestId)
    self.assertEqual(instance.metaCallerGrpcKhaleesiGate, requestMetadata.grpcCaller.khaleesiGate)
    self.assertEqual(
      instance.metaCallerGrpcKhaleesiService,
      requestMetadata.grpcCaller.khaleesiService,
    )
    self.assertEqual(instance.metaCallerGrpcGrpcService    , requestMetadata.grpcCaller.grpcService)
    self.assertEqual(instance.metaCallerGrpcGrpcMethod     , requestMetadata.grpcCaller.grpcMethod)
    self.assertEqual(instance.metaCallerGrpcPodId          , requestMetadata.grpcCaller.podId)

  def _createRequestMetadata(self, *, string: MagicMock) -> RequestMetadata :
    """Utility for creating fully populated request metadata objects."""
    string.return_value    = 'parsed-string'
    grpc = RequestMetadata()

    grpc.grpcCaller.requestId       = 'grpc-request'
    grpc.grpcCaller.khaleesiGate    = 'grpc-gate'
    grpc.grpcCaller.khaleesiService = 'grpc-service'
    grpc.grpcCaller.grpcService     = 'grpc-service'
    grpc.grpcCaller.grpcMethod      = 'grpc-method'
    grpc.grpcCaller.podId           = 'grpc-pod'

    return grpc
