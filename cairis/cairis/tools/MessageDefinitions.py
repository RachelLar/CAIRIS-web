from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger

from tools import PseudoClasses
from tools.SessionValidator import get_logger


__author__ = 'Robin Quetin'

import ModelDefinitions

def gen_message_fields(class_ref, *prop_class_refs):
    resource_fields = {
        "session_id": fields.String,
        "object": fields.Nested(class_ref.resource_fields),
    }

    for count, prop_class_ref in enumerate(prop_class_refs):
        try:
            resource_fields['property_%d'%count] = fields.List(fields.Nested(prop_class_ref.resource_fields))
        except AttributeError:
            get_logger().warning('Unable to load property class reference for %s' % class_ref.__name__)

    return resource_fields

class DefaultMessage(object):
    required = ['object']

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.AssetEnvironmentPropertiesModel.__name__
)
# endregion
class AssetEnvironmentPropertiesMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.AssetEnvironmentPropertiesModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.AssetModel.__name__,
    property_0=ModelDefinitions.AssetEnvironmentPropertiesModel.__name__
)
# endregion
class AssetMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.AssetModel, ModelDefinitions.AssetEnvironmentPropertiesModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=PseudoClasses.EnvironmentModel.__name__
)
# endregion
class EnvironmentMessage(DefaultMessage):
    resource_fields = gen_message_fields(PseudoClasses.EnvironmentModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.GoalModel.__name__
)
# endregion
class GoalMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.GoalModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.RequirementModel.__name__
)
# endregion
class RequirementMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.RequirementModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.RiskModel.__name__
)
# endregion
class RiskMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.RiskModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.RoleModel.__name__
)
# endregion
class RoleMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.RoleModel)
    required = DefaultMessage.required