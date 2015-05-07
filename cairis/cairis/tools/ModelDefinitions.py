from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger
from Goal import Goal
from MisuseCase import MisuseCase
from MisuseCaseEnvironmentProperties import MisuseCaseEnvironmentProperties
from Requirement import Requirement
from Risk import Risk

__author__ = 'Robin Quetin'


def gen_class_metadata(class_ref):
    return {
        "enum": [class_ref.__module__+'.'+class_ref.__name__]
    }

@swagger.model
class AssetEnvironmentPropertiesModel(object):
    resource_fields = {
        "theAssociations": fields.List,
        "theProperties": fields.Integer,
        "theRationale": fields.List(fields.String),
        "theEnvironmentName": fields.String
    }

@swagger.model
@swagger.nested(
    envProps=AssetEnvironmentPropertiesModel.__name__
)
class AssetModel(object):
    resource_fields = {
        "theDescription": fields.String,
        "theSignificance": fields.String,
        "theId": fields.Integer,
        "theTags": fields.List(fields.String),
        "theCriticalRationale": fields.String,
        "theInterfaces": fields.List(fields.String),
        "theType": fields.String,
        "theName": fields.String,
        "isCritical": fields.Integer,
        "theShortCode": fields.String,
        "theEnvironmentProperties": fields.List(fields.Nested(AssetEnvironmentPropertiesModel.resource_fields))
    }
    required = [
        "theDescription", "theSignificance", "theId", "theTags", "theCriticalRationale",
        "theInterfaces", "theType", "theName", "isCritical", "theShortCode", "theEnvironmentProperties"
    ]

@swagger.model
class CImportParams(object):
    resource_fields = {
        'file_contents': fields.String,
        'type': fields.String,
        'overwrite': fields.Integer
    }
    required = ['file_contents', 'type']

@swagger.model
class GoalEnvironmentProperties(object):
    resource_fields = {
        "theCategory": fields.String,
        "theConcernAssociations": fields.List(fields.String),
        "theConcerns": fields.List(fields.String),
        "theDefinition": fields.String,
        "theEnvironmentName": fields.String,
        "theFitCriterion": fields.String,
        "theGoalRefinements": fields.List(fields.String),
        "theIssue": fields.String,
        "theLabel": fields.String,
        "thePriority": fields.String,
        "theSubGoalRefinements": fields.List(fields.String)
    }

    required = [
        "theCategory",
        "theConcernAssociations",
        "theConcerns",
        "theDefinition",
        "theEnvironmentName",
        "theFitCriterion",
        "theGoalRefinements",
        "theIssue",
        "theLabel",
        "thePriority",
        "theSubGoalRefinements"
    ]

@swagger.model
@swagger.nested(
    theEnvironmentProperties=GoalEnvironmentProperties.__name__
)
class GoalModel(object):
    resource_fields = {
        "__python_obj__": fields.String,
        "theColour": fields.String,
        "theEnvironmentDictionary": {
            "_key_": fields.List(fields.Nested(GoalEnvironmentProperties.resource_fields))
        },
        "theEnvironmentProperties": fields.List(fields.Nested(GoalEnvironmentProperties.resource_fields)),
        "theId": fields.Integer,
        "theName": fields.String,
        "theOriginator": fields.String,
        "theTags": fields.List(fields.String)
    }
    required = ["__python_obj__", "theColour","theEnvironmentProperties","theId","theName","theOriginator","theTags"]
    swagger_metadata = {
        "__python_obj__" : gen_class_metadata(Goal)
    }

@swagger.model
class MisuseCaseEnvironmentPropertiesModel(object):
    resource_fields = {
        "__python_obj__": fields.String(default=MisuseCaseEnvironmentProperties.__name__),
        "theDescription": fields.String,
        "theEnvironmentName": fields.String
    }
    required = ["__python_obj__"]

@swagger.model
@swagger.nested(
    MisuseCaseEnvironmentProperties=MisuseCaseEnvironmentPropertiesModel.__name__
)
class MisuseCaseModel(object):
    resource_fields = {
        "__python_obj__": fields.String(default=MisuseCase.__name__),
        "theEnvironmentDictionary": {
            "_key_": fields.Nested(MisuseCaseEnvironmentPropertiesModel.resource_fields)
        },
        "theVulnerabilityName": fields.String,
        "theId": fields.Integer,
        "theThreatName": fields.String,
        "theRiskName": fields.String,
        "theName": fields.String,
        "theEnvironmentProperties": fields.List(fields.Nested(MisuseCaseEnvironmentPropertiesModel.resource_fields))
    }

    required = ["__python_obj__"]

@swagger.model
class RequirementAttributesModel(object):
    resource_fields = {
        "originator": fields.String,
        "supportingMaterial": fields.String,
        "fitCriterion": fields.String,
        "asset": fields.String,
        "rationale": fields.String,
        "type": fields.String
    }

@swagger.model
@swagger.nested(
    dirtyAttrs=RequirementAttributesModel.__name__,
    attrs=RequirementAttributesModel.__name__
)
class RequirementModel(object):
    resource_fields = {
        "__python_obj__": fields.String(Requirement.__name__),
        "theId": fields.Integer,
        "dirtyAttrs": fields.Nested(RequirementAttributesModel.resource_fields),
        "attrs": fields.Nested(RequirementAttributesModel.resource_fields),
        "theName": fields.String,
        "theLabel": fields.String,
        "theDescription": fields.String,
        "thePriority": fields.Integer,
        "theVersion": fields.Integer
    }
    required = ["__python_obj__", "theId", "dirtyAttrs", "attrs", "theName", "theLabel", "theDescription", "thePriority", "theVersion"]

@swagger.model
@swagger.nested(
    MisuseCaseModel=MisuseCaseModel.__name__
)
class RiskModel(object):
    resource_fields = {
        "__python_obj__": fields.String(default=Risk.__name__),
        "theVulnerabilityName": fields.String,
        "theId": fields.Integer,
        "theMisuseCase": fields.Nested(MisuseCaseModel.resource_fields),
        "theTags": fields.List(fields.Nested(fields.String)),
        "theThreatName": fields.String,
        "theName": fields.String
    }
    required = ["__python_obj__", "theVulnerabilityName", "theId", "theMisuseCase", "theTags", "theThreatName", "theName"]

@swagger.model
class UserConfigModel(object):
    resource_fields = {
        "user": fields.String,
        "passwd": fields.String,
        "db": fields.String,
        "host": fields.String,
        "port": fields.Integer,
        "jsonPrettyPrint": fields.String
    }

    required = ["user", "passwd", "db", "host", "port"]
    swagger_metadata = {
        'jsonPrettyPrint':
            {
                'enum': ['on', 'off']
            }
    }