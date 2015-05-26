from flask.ext.restful import fields
from flask.ext.restful_swagger import swagger

from Asset import Asset
from AssetEnvironmentProperties import AssetEnvironmentProperties
from Attacker import Attacker
from AttackerEnvironmentProperties import AttackerEnvironmentProperties
from Goal import Goal
from GoalEnvironmentProperties import GoalEnvironmentProperties
from MisuseCase import MisuseCase
from MisuseCaseEnvironmentProperties import MisuseCaseEnvironmentProperties
from Requirement import Requirement
from Risk import Risk
from Role import Role
from ThreatEnvironmentProperties import ThreatEnvironmentProperties
from ValueType import ValueType
from Vulnerability import Vulnerability
from VulnerabilityEnvironmentProperties import VulnerabilityEnvironmentProperties
from tools.PseudoClasses import EnvironmentTensionModel, SecurityAttribute


__author__ = 'Robin Quetin'

obj_id_field = "__python_obj__"
def gen_class_metadata(class_ref):
    return {
        "enum": [class_ref.__module__+'.'+class_ref.__name__]
    }

@swagger.model
@swagger.nested(attributes=SecurityAttribute.__name__)
class AssetEnvironmentPropertiesModel(object):
    def __init__(self, env_name='', associations=[], attributes=[]):
        self.environment = env_name
        self.associations = associations
        self.attributes = attributes
        self.attributesDictionary = {}

    def json_prepare(self):
        self.attributes = self.attributesDictionary.values()
        self.attributesDictionary = {}
        for idx in range(0, len(self.associations)):
            self.associations[idx] = list(self.associations[idx])

    resource_fields = {
        "__python_obj__": fields.String,
        "theAssociations": fields.List(fields.List(fields.String)),
        "theProperties": fields.List(fields.Nested(SecurityAttribute.resource_fields)),
        "theEnvironmentName": fields.String,
        "theRationale": fields.List(fields.String)
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    required.remove("theRationale")
    swagger_metadata = {
        obj_id_field: gen_class_metadata(AssetEnvironmentProperties)
    }

@swagger.model
@swagger.nested(
    theEnvironmentProperties=AssetEnvironmentPropertiesModel.__name__
)
class AssetModel(object):
    resource_fields = {
        obj_id_field: fields.String,
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
    required = resource_fields.keys()
    required.remove(obj_id_field)
    swagger_metadata = {
        obj_id_field : gen_class_metadata(Asset)
    }


@swagger.model
class CapabilityModel(object):
    resource_fields = {
        "name": fields.String,
        "value": fields.String
    }
    required = resource_fields.keys()

@swagger.model
@swagger.nested(
    theCapabilities=CapabilityModel.__name__
)
class AttackerEnvironmentPropertiesModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        'theMotives': fields.List(fields.String),
        'theRoles': fields.List(fields.String),
        'theCapabilities': fields.List(fields.Nested(CapabilityModel.resource_fields)),
        'theEnvironmentName': fields.String,
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    swagger_metadata = {
        obj_id_field: gen_class_metadata(AttackerEnvironmentProperties)
    }

@swagger.model
@swagger.nested(
    theEnvironmentProperties=AttackerEnvironmentPropertiesModel.__name__
)
class AttackerModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        'theEnvironmentDictionary': fields.List(fields.Nested(AttackerEnvironmentPropertiesModel.resource_fields)),
        'theDescription': fields.String,
        'theId': fields.Integer,
        'theTags': fields.List(fields.String),
        'isPersona': fields.Integer,
        'theName': fields.String,
        'theImage': fields.String,
        'theEnvironmentProperties': fields.List(fields.Nested(AttackerEnvironmentPropertiesModel.resource_fields)),
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    required.remove('theEnvironmentDictionary')
    swagger_metadata = {
        obj_id_field: gen_class_metadata(Attacker)
    }

@swagger.model
class CImportParams(object):
    resource_fields = {
        'session_id': fields.String,
        'file_contents': fields.String,
        'type': fields.String,
        'overwrite': fields.Integer
    }
    required = ['file_contents', 'type']

@swagger.model
@swagger.nested(
    theTensions=EnvironmentTensionModel.__name__,
)
class EnvironmentModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        "theId": fields.Integer,
        "theName": fields.String,
        "theShortCode": fields.String,
        "theDescription": fields.String,
        "theEnvironments": fields.List(fields.String),
        "theDuplicateProperty": fields.String,
        "theOverridingEnvironment": fields.String,
        "theTensions": fields.List(fields.Nested(EnvironmentTensionModel.resource_fields)),
        }
    required = resource_fields.keys()
    required.remove(obj_id_field)

@swagger.model
class GoalEnvironmentPropertiesModel(object):
    resource_fields = {
        obj_id_field: fields.String,
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
    required = resource_fields.keys()
    swagger_metadata = {
        obj_id_field : gen_class_metadata(GoalEnvironmentProperties)
    }

@swagger.model
@swagger.nested(
    theEnvironmentProperties=GoalEnvironmentPropertiesModel.__name__
)
class GoalModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        "theColour": fields.String,
        "theEnvironmentDictionary": fields.List,
        "theEnvironmentProperties": fields.List(fields.Nested(GoalEnvironmentPropertiesModel.resource_fields)),
        "theId": fields.Integer,
        "theName": fields.String,
        "theOriginator": fields.String,
        "theTags": fields.List(fields.String)
    }
    required = [obj_id_field, "theColour","theEnvironmentProperties","theId","theName","theOriginator","theTags"]
    swagger_metadata = {
        obj_id_field : gen_class_metadata(Goal)
    }

@swagger.model
class MisuseCaseEnvironmentPropertiesModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        "theDescription": fields.String,
        "theEnvironmentName": fields.String
    }

    required = [obj_id_field, "theDescription", "theEnvironmentName"]

    swagger_metadata = {
        obj_id_field : gen_class_metadata(MisuseCaseEnvironmentProperties)
    }

@swagger.model
@swagger.nested(
    MisuseCaseEnvironmentProperties=MisuseCaseEnvironmentPropertiesModel.__name__
)
class MisuseCaseModel(object):
    resource_fields = {
        obj_id_field: fields.String,
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

    required = [obj_id_field]
    swagger_metadata = {
        obj_id_field : gen_class_metadata(MisuseCase)
    }

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
        obj_id_field: fields.String,
        "theId": fields.Integer,
        "dirtyAttrs": fields.Nested(RequirementAttributesModel.resource_fields),
        "attrs": fields.Nested(RequirementAttributesModel.resource_fields),
        "theName": fields.String,
        "theLabel": fields.String,
        "theDescription": fields.String,
        "thePriority": fields.Integer,
        "theVersion": fields.Integer
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    swagger_metadata = {
        obj_id_field : gen_class_metadata(Requirement)
    }

@swagger.model
@swagger.nested(
    MisuseCaseModel=MisuseCaseModel.__name__
)
class RiskModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        "theVulnerabilityName": fields.String,
        "theId": fields.Integer,
        "theMisuseCase": fields.Nested(MisuseCaseModel.resource_fields),
        "theTags": fields.List(fields.Nested(fields.String)),
        "theThreatName": fields.String,
        "theName": fields.String
    }
    required = [obj_id_field, "theVulnerabilityName", "theId", "theMisuseCase", "theTags", "theThreatName", "theName"]
    swagger_metadata = {
        obj_id_field : gen_class_metadata(Risk)
    }

@swagger.model
class RoleModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        "theId": fields.Integer,
        "theName": fields.String,
        "theType": fields.String,
        "theShortCode": fields.String,
        "theDescription": fields.String,
        "theEnvironmentProperties": None
    }

    required = resource_fields.keys()
    required.remove(obj_id_field)
    required.remove("theEnvironmentProperties")

    swagger_metadata = {
        obj_id_field : gen_class_metadata(Role)
    }

@swagger.model
class RoleEnvironmentPropertiesModel(object):
    resource_fields = {
        "theEnvironmentName": fields.String,
        "theResponses": fields.List(fields.List(fields.String)),
        "theCountermeasures": fields.List(fields.String)
    }
    required = resource_fields.keys()

@swagger.model
@swagger.nested(
    theProperties=SecurityAttribute.__name__
)
class ThreatEnvironmentPropertiesModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        'theAssets': fields.List(fields.String),
        'theLikelihood': fields.String,
        'theEnvironmentName': fields.String,
        'theAttackers': fields.List(fields.String),
        'theRationale': fields.List(fields.String),
        'theProperties': fields.List(fields.Nested(SecurityAttribute.resource_fields)),
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    required.remove('theRationale')
    swagger_metadata = {
        obj_id_field : gen_class_metadata(ThreatEnvironmentProperties),
        'theLikelihood' : {
            "enum": ['Incredible','Improbable','Remote','Occasional','Probable', 'Frequent']
        }
    }

@swagger.model
@swagger.nested(
    theEnvironmentProperties=ThreatEnvironmentPropertiesModel.__name__
)
class ThreatModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        'theEnvironmentDictionary': fields.List(fields.String),
        'theId': fields.Integer,
        'theTags': fields.List(fields.String),
        'theThreatPropertyDictionary': fields.List(fields.String),
        'theThreatName': fields.String,
        'theType': fields.String,
        'theMethod': fields.String,
        'theEnvironmentProperties': fields.List(fields.Nested(ThreatEnvironmentPropertiesModel.resource_fields)),
        'likelihoodLookup': fields.List(fields.String),
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    required.remove('theThreatPropertyDictionary')
    required.remove('theEnvironmentDictionary')
    required.remove('likelihoodLookup')

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
    required = resource_fields.keys()
    required.remove("jsonPrettyPrint")
    swagger_metadata = {
        'jsonPrettyPrint':
            {
                'enum': ['on', 'off']
            }
    }

@swagger.model
class ValueTypeModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        'theScore': fields.Integer,
        'theId': fields.Integer,
        'theRationale': fields.String,
        'theType': fields.String,
        'theName': fields.String,
        'theDescription': fields.String,
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    swagger_metadata = {
        obj_id_field: gen_class_metadata(ValueType),
        "theType": {
            "enum": ['asset_value','threat_value','risk_class','countermeasure_value','capability','motivation','asset_type','threat_type','vulnerability_type','severity','likelihood','access_right','protocol','privilege','surface_type']
        }
    }

@swagger.model
class VulnerabilityEnvironmentPropertiesModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        "theAssets": fields.List(fields.String),
        "theEnvironmentName": fields.String,
        "theSeverity": fields.String
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    swagger_metadata = {
        obj_id_field : gen_class_metadata(VulnerabilityEnvironmentProperties),
        "theSeverity": {
            "enum": ['Negligible', 'Marginal', 'Critical','Catastrophic']
        }
    }

@swagger.model
@swagger.nested(
    theEnvironmentProperties=VulnerabilityEnvironmentPropertiesModel.__name__,
    theEnvironmentDictionary=VulnerabilityEnvironmentPropertiesModel.__name__
)
class VulnerabilityModel(object):
    resource_fields = {
        obj_id_field: fields.String,
        'theEnvironmentDictionary': fields.List(fields.Nested(VulnerabilityEnvironmentPropertiesModel.resource_fields)),
        'theVulnerabilityName': fields.String,
        'theVulnerabilityType': fields.String,
        'theTags': fields.List(fields.String),
        'theVulnerabilityDescription': fields.String,
        'theVulnerabilityId': fields.Integer,
        'severityLookup': fields.List(fields.String),
        'theEnvironmentProperties': fields.List(fields.Nested(VulnerabilityEnvironmentPropertiesModel.resource_fields))
    }
    required = resource_fields.keys()
    required.remove(obj_id_field)
    required.remove('theEnvironmentDictionary')
    required.remove('severityLookup')
    swagger_metadata = {
        obj_id_field: gen_class_metadata(Vulnerability),
        'theVulnerabilityType' : {
            "enum": ['Configuration', 'Design', 'Implementation']
        }
    }