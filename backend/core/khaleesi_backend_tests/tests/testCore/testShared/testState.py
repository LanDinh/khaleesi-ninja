"""Test the exceptions."""

# khaleesi.ninja.
from khaleesi.core.shared.state import STATE
from khaleesi.core.testUtil.testCase import SimpleTestCase
from khaleesi.proto.core_pb2 import User, RequestMetadata
from khaleesi.proto.core_sawmill_pb2 import Query


class StateTestCase(SimpleTestCase):
  """Test the exceptions."""

  def testReset(self) -> None :
    """Test resetting the state."""
    for userLabel, userType in  User.UserType.items():
      with self.subTest(userType = userLabel):
        # Prepare data.
        STATE.request.httpCaller.requestId = 'http-request-id'
        STATE.request.grpcCaller.requestId = 'grpc-request-id'
        STATE.request.user.id              = 'user'
        STATE.request.user.type            = userType
        STATE.queries.append(Query())
        # Execute test.
        STATE.reset()
        # Assert result.
        self.assertEqual(STATE.request.httpCaller.requestId, 'UNKNOWN')
        self.assertEqual(STATE.request.grpcCaller.requestId, 'system')
        self.assertEqual(STATE.request.user.id             , 'UNKNOWN')
        self.assertEqual(STATE.request.user.type           , User.UserType.UNKNOWN)
        self.assertEqual(len(STATE.queries)                , 0)

  def testCopyFrom(self) -> None :
    """Test copying the state."""
    # Prepare data.
    request = RequestMetadata()
    request.httpCaller.requestId = 'http-request-id'
    request.grpcCaller.requestId = 'grpc-request-id'
    request.user.id              = 'user'
    queries                      = [ Query() ]
    for userLabel, userType in  User.UserType.items():
      with self.subTest(userType = userLabel):
        STATE.reset()
        request.user.type = userType
        # Execute test.
        STATE.copyFrom(request = request, queries = queries)
        # Assert result.
        self.assertEqual(STATE.request.httpCaller.requestId, request.httpCaller.requestId)
        self.assertEqual(STATE.request.grpcCaller.requestId, request.grpcCaller.requestId)
        self.assertEqual(STATE.request.user.id             , request.user.id)
        self.assertEqual(STATE.request.user.type           , userType)
        self.assertEqual(len(STATE.queries)                , 1)
