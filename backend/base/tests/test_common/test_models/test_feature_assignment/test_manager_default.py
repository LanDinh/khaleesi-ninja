"""The tests for the custom role assignment DefaultManager."""

# Python.
from unittest.mock import patch, MagicMock

# khaleesi.ninja.
from common.models import Feature, FeatureAssignment, Manager, Role
from common.models.auth.feature_assignment.feature_assignment_state import \
  FeatureAssignmentState
from common.service_type import ServiceType
from test_util.test import SimpleTestCase, TestCase
from test_util.models.user import TestUserUnitMixin, TestUserIntegrationMixin


class FeatureAssignmentDefaultManagerUnitTests(SimpleTestCase, TestUserUnitMixin):
  """The unit tests for the custom role assignment DefaultManager."""

  @patch.object(Manager, 'get_queryset', return_value = MagicMock())
  def test_create(self, base_queryset: MagicMock) -> None :
    """Test role assignment creation."""
    for service in ServiceType:
      with self.subTest(service = service):
        # Prepare data.
        name = 'test'
        base_queryset.return_value.create = MagicMock()
        role = Role(service = service.name)
        feature = Feature(service = service.name, name = name)
        # Perform test.
        FeatureAssignment.objects.create(role = role, feature = feature)
        # Assert result.
        base_queryset.return_value.create.assert_called_once_with(role = role, feature = feature)


# noinspection PyUnresolvedReferences,PyTypeHints
class FeatureAssignmentDefaultManagerIntegrationTests(TestCase, TestUserIntegrationMixin):
  """The integration tests for the custom role assignment DefaultManager."""

  def test_create(self) -> None :
    """Test role assignment creation."""
    for service in ServiceType:
      for role_name in ['', 'test']:
        with self.subTest(service = service, role_name = role_name):
          # Prepare data.
          feature_name = 'test'
          Role.migrations.create(service = service, name = role_name)
          role: Role = Role.objects.get(service = service.name, name = role_name)
          Feature.objects.get_or_create(service = service, name = feature_name)
          feature: Feature = Feature.objects.get(service = service.name, name = feature_name)
          # Perform test.
          FeatureAssignment.objects.create(role = role, feature = feature)
          # Assert result.
          result: FeatureAssignment = role.featureassignment_set.get(
              feature__service = service.name,
              feature__name = feature_name,
          )
          self.assertEqual(role, result.role)
          self.assertEqual(feature, result.feature)
          self.assertEqual(FeatureAssignmentState.ALPHA.name, result.state)
          role.delete()
          feature.delete()
