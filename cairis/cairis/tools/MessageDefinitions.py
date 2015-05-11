from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger

__author__ = 'Robin Quetin'

import ModelDefinitions

def gen_message_fields(class_ref):
    return {
        "session_id": fields.String,
        "object": fields.Nested(class_ref.resource_fields)
    }

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
    object=ModelDefinitions.AssetModel.__name__
)
# endregion
class AssetMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.AssetModel)
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