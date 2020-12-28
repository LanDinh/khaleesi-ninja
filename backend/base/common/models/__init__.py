"""Base common models."""

# pylint: disable=useless-import-alias

from common.models.manager import Manager as Manager
from common.models.model import Model as Model

from common.models.feature.model import Feature as Feature
from common.models.feature_assignment.model import FeatureAssignment as FeatureAssignment
from common.models.role.model import Role as Role
from common.models.role_assignment.model import RoleAssignment as RoleAssignment
from common.models.user.model import User as User
