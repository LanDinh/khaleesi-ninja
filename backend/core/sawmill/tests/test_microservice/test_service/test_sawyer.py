"""Test the core-sawmill sawyer service."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from khaleesi.proto.core_pb2 import User
from khaleesi.proto.core_sawmill_pb2 import EventResponse as GrpcEventResponse, LogFilter
from microservice.models import Event
from khaleesi.core.test_util.test_case import SimpleTestCase
from microservice.service.sawyer import Service

class SawyerServiceTestCase(SimpleTestCase):
  """Test the core-sawmill sawyer service."""

  service = Service()

  @patch.object(Event.objects, 'filter')
  def test_get_events(self, db_events: MagicMock) -> None :
    """Test getting logged events."""
    # Prepare data.
    db_event = MagicMock()
    db_event.to_grpc_event_response.return_value = GrpcEventResponse()
    db_events.return_value = [ db_event ]
    # Execute tests.
    result = self.service.GetEvents(LogFilter(), MagicMock())
    # Assert result.
    self.assertEqual(1, len(result.events))
    db_events.assert_called_once_with(meta_user_type = User.UserType.SYSTEM)
    db_event.to_grpc_event_response.assert_called_once_with()
