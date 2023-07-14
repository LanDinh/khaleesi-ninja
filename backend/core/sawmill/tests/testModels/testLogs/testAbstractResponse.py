"""Test the request logs."""

# Python.
from datetime import timezone, timedelta, datetime
from unittest.mock import patch, MagicMock

# gRPC.
from grpc import StatusCode

# khaleesi.ninja.
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import (
  Response as GrpcResponse,
  GrpcRequestResponse as GrpcGrpcRequestResponse,
)
from microservice.testUtil import ModelResponseMetadataMixin
from tests.models import OldResponseMetadata


class ResponseMetadataTestCase(ModelResponseMetadataMixin, SimpleTestCase):
  """Test the request logs models."""

  def testInitialValues(self) -> None :
    """Test initial values."""
    # Execute result.
    response = OldResponseMetadata()
    # Assert result.
    self.assertTrue(response.isInProgress)
    self.assertEqual('IN_PROGRESS', response.metaResponseStatus)
    self.assertEqual(timedelta(0) , response.loggedDuration)
    self.assertEqual(timedelta(0) , response.reportedDuration)
    self.assertEqual(timedelta(0) , response.metaChildDuration)
    self.assertEqual(0            , response.childDurationRelative)

  def testChildDurationRelative(self) -> None :
    """Test child duration."""
    # Prepare data.
    now = datetime.now().replace(tzinfo = timezone.utc)
    response = OldResponseMetadata()
    response.metaLoggedTimestamp         = now
    response.metaResponseLoggedTimestamp = now + timedelta(minutes = 10)
    response.metaChildDuration           = timedelta(minutes = 1)
    response.metaResponseStatus          = 'OK'
    # Execute test.
    result = response.childDurationRelative
    # Assert result.
    self.assertEqual(0.1, result)

  @patch('microservice.models.logs.abstractResponse.parseTimestamp')
  def testLogResponse(self, timestamp: MagicMock) -> None :
    """Test logging a response."""
    for status in StatusCode:
      with self.subTest(status = status.name):
        # Prepare data.
        request = self.getModelForResponseSaving(modelType = OldResponseMetadata)
        timestamp.return_value = request.metaResponseLoggedTimestamp
        response = GrpcResponse()
        response.status = status.name
        response.timestamp.FromDatetime(request.metaResponseLoggedTimestamp)
        # Execute test.
        request.logResponse(grpcResponse = response)
        # Assert result.
        self.assertEqual(response.status, request.metaResponseStatus)
        self.assertEqual(
          response.timestamp.ToDatetime().replace(tzinfo = timezone.utc),
          request.metaResponseReportedTimestamp,
        )
        self.assertFalse(request.isInProgress)
        self.assertLess(timedelta(0), request.loggedDuration)
        self.assertLess(timedelta(0), request.reportedDuration)

  @patch('microservice.models.logs.abstractResponse.parseTimestamp')
  def testLogEmptyResponse(self, timestamp: MagicMock) -> None :
    """Test logging a response."""
    # Prepare data.
    request = self.getModelForResponseSaving(modelType = OldResponseMetadata)
    timestamp.return_value = datetime.min.replace(tzinfo = timezone.utc)
    response = GrpcResponse()
    # Execute test.
    request.logResponse(grpcResponse = response)
    # Assert result.
    self.assertIn('Response status', request.metaResponseLoggingErrors)
    self.assertFalse(request.isInProgress)
    self.assertLess(timedelta(0) , request.loggedDuration)
    self.assertEqual(timedelta(0), request.reportedDuration)

  def testToGrpc(self) -> None :
    """Test that general mapping to gRPC works."""
    for userLabel, userType in User.UserType.items():
      for status in StatusCode:
        with self.subTest(user = userLabel, status = status.name):
          # Prepare data.
          request = OldResponseMetadata(
            **self.modelFullRequestMetadata(user = userType, status = status),
          )
          result = GrpcGrpcRequestResponse()
          # Execute test.
          request.responseToGrpc(
            metadata  = result.responseMetadata,
            response  = result.response,
            processed = result.processedResponse,
          )
          # Assert result.
          self.assertGrpcResponseMetadata(
            model                 = request,
            grpcResponse          = result.response,
            grpcResponseResponse  = result.responseMetadata,
            grpcResponseProcessed = result.processedResponse,
          )


  def testEmptyToGrpc(self) -> None :
    """Test that mapping to gRPC for empty events works."""
    # Prepare data.
    request = OldResponseMetadata(**self.modelEmptyRequestMetadata())
    result  = GrpcGrpcRequestResponse()
    # Execute test.
    request.responseToGrpc(
      metadata  = result.responseMetadata,
      response  = result.response,
      processed = result.processedResponse,
    )
    # Assert result.
    self.assertIsNotNone(result)
    self.assertEqual(0, result.processedResponse.loggedDuration.nanos)
    self.assertEqual(0, result.processedResponse.reportedDuration.nanos)
