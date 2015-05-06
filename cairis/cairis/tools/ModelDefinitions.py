from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger

__author__ = 'Robin Quetin'


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
    _key_=GoalEnvironmentProperties.__name__
)
class GoalEnvironmentPropertiesDictionary(object):
    resource_fields = {
        "_key_": fields.Nested(GoalEnvironmentProperties.resource_fields)
    }
    required = ["_key_"]

@swagger.model
@swagger.nested(
    theEnvironmentDictionary=GoalEnvironmentPropertiesDictionary.__name__,
    theEnvironmentProperties=GoalEnvironmentProperties.__name__
)
class GoalModel(object):
    resource_fields = {
        "theColour": fields.String,
        "theEnvironmentDictionary": fields.List(fields.Nested(GoalEnvironmentProperties.resource_fields)),
        "theEnvironmentProperties": fields.List(fields.Nested(GoalEnvironmentProperties.resource_fields)),
        "theId": fields.Integer,
        "theName": fields.String,
        "theOriginator": fields.String,
        "theTags": fields.List(fields.String)
    }
    required = ["theColour","theEnvironmentProperties","theId","theName","theOriginator","theTags"]

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
        "theId": fields.Integer,
        "dirtyAttrs": fields.Nested(RequirementAttributesModel.resource_fields),
        "attrs": fields.Nested(RequirementAttributesModel.resource_fields),
        "theName": fields.String,
        "theLabel": fields.String,
        "theDescription": fields.String,
        "thePriority": fields.Integer,
        "theVersion": fields.Integer
    }
    required = ["theId", "dirtyAttrs", "attrs", "theName", "theLabel", "theDescription", "thePriority", "theVersion"]

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