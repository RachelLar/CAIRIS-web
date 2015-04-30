from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger
from PropertyHolder import PropertyHolder

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
        "description": fields.String,
        "significance": fields.String,
        "id": fields.Integer,
        "tags": fields.List(fields.String),
        "cRationale": fields.String,
        "interfaces": fields.List(fields.String),
        "type": fields.String,
        "name": fields.String,
        "isCritical": fields.Integer,
        "shortcode": fields.String,
        "envProps": fields.List(fields.Nested(AssetEnvironmentPropertiesModel.resource_fields))
    }
    required = [
        "description", "significance", "id", "tags", "cRationale",
        "interfaces", "type", "name", "isCritical", "shortcode", "envProps"
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