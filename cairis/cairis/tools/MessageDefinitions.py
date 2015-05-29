from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger
from tools import PseudoClasses

__author__ = 'Robin Quetin'

import ModelDefinitions

def gen_message_fields(class_ref):
    resource_fields = {
        "session_id": fields.String,
        "object": fields.Nested(class_ref.resource_fields),
    }
    return resource_fields

def gen_message_multival_fields(class_ref):
    resource_fields = {
        "session_id": fields.String,
        "object": fields.List(fields.Nested(class_ref.resource_fields))
    }

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
    resource_fields = gen_message_multival_fields(ModelDefinitions.AssetEnvironmentPropertiesModel)
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
    object=ModelDefinitions.AttackerModel.__name__,
)
# endregion
class AttackerMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.AttackerModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.CImportParams.__name__
)
# endregion
class CImportMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.CImportParams)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.EnvironmentModel.__name__
)
# endregion
class EnvironmentMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.EnvironmentModel)
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
    object=PseudoClasses.ProjectSettings.__name__
)
# endregion
class ProjectMessage(DefaultMessage):
    resource_fields = gen_message_fields(PseudoClasses.ProjectSettings)
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
    object=ModelDefinitions.RoleModel.__name__,
    property_0=ModelDefinitions.RoleEnvironmentPropertiesModel.__name__
)
# endregion
class RoleMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.RoleModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.ThreatModel.__name__
)
# endregion
class ThreatMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.ThreatModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.ValueTypeModel.__name__
)
# endregion
class ValueTypeMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.ValueTypeModel)
    required = DefaultMessage.required

# region Swagger Doc
@swagger.model
@swagger.nested(
    object=ModelDefinitions.VulnerabilityModel.__name__
)
# endregion
class VulnerabilityMessage(DefaultMessage):
    resource_fields = gen_message_fields(ModelDefinitions.VulnerabilityModel)
    required = DefaultMessage.required